from datetime import datetime, timedelta
from .models import Booking
from rest_framework import status
from django.db import transaction
from users.models import LSAProfile
from rest_framework.views import APIView
from .serializers import BookingSerializer
from rest_framework.response import Response
from rest_framework.permissions import AllowAny


class BookingView(APIView):

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = BookingSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        """Using an atomic transaction ensures that the booking operation is completed
            as a single unit. The LSA row will be locked with select_for_update() before
            checking for overlapping bookings and will prevent concurrent requests from
            booking the same LSA for the same time slot. If any operation inside the
            transaction fails, all database changes are rolled back."""
        try:
            with transaction.atomic():
                lsa = (
                    LSAProfile.objects
                    .select_for_update()
                    .get(
                        pk=serializer.validated_data["lsa"].pk
                    )
                )
                if not lsa.is_active:
                    return Response(
                        {
                            "lsa": [
                                "Cannot book an inactive LSA profile."
                            ]
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                booking_data = serializer.validated_data.copy()
                booking_data["lsa"] = lsa

                start_dt = datetime.combine(booking_data["booking_date"], booking_data["start_time"])
                end_dt = datetime.combine(booking_data["booking_date"], booking_data["end_time"])
                if booking_data["end_time"] <= booking_data["start_time"]:
                    end_dt += timedelta(days=1)

                candidates = Booking.objects.filter(
                    lsa=lsa,
                    booking_date__range=[booking_data["booking_date"] - timedelta(days=1), booking_data["booking_date"] + timedelta(days=1)],
                    status__in=Booking.BLOCKING_STATUSES,
                )

                is_overlapping = False
                for b in candidates:
                    b_start = datetime.combine(b.booking_date, b.start_time)
                    b_end = datetime.combine(b.booking_date, b.end_time)
                    if b.end_time <= b.start_time:
                        b_end += timedelta(days=1)
                    if b_start < end_dt and b_end > start_dt:
                        is_overlapping = True
                        break

                if is_overlapping:
                    return Response(
                        {
                            "booking": [
                                "This LSA already has a booking "
                                "during the selected time."
                            ]
                        },
                        status=status.HTTP_409_CONFLICT,
                    )

                parent = booking_data["parent"]
                parent_candidates = Booking.objects.filter(
                    parent=parent,
                    booking_date__range=[booking_data["booking_date"] - timedelta(days=1), booking_data["booking_date"] + timedelta(days=1)],
                    status__in=Booking.BLOCKING_STATUSES,
                )

                is_parent_overlapping = False
                for b in parent_candidates:
                    b_start = datetime.combine(b.booking_date, b.start_time)
                    b_end = datetime.combine(b.booking_date, b.end_time)
                    if b.end_time <= b.start_time:
                        b_end += timedelta(days=1)
                    if b_start < end_dt and b_end > start_dt:
                        is_parent_overlapping = True
                        break

                if is_parent_overlapping:
                    return Response(
                        {
                            "booking": [
                                "You already have another booking "
                                "during the selected time."
                            ]
                        },
                        status=status.HTTP_409_CONFLICT,
                    )
                booking = Booking.objects.create(
                    **booking_data
                )
        except LSAProfile.DoesNotExist:
            return Response(
                {
                    "lsa": [
                        "LSA profile does not exist."
                    ]
                },
                status=status.HTTP_404_NOT_FOUND,
            )
            
        return Response(
            {
                "message": "Booking created successfully!",
                "data": BookingSerializer(booking).data,
            },
            status=status.HTTP_201_CREATED,
        )