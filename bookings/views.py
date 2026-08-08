from django.db import transaction
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from users.models import LSAProfile
from .models import Booking
from .serializers import BookingSerializer


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
        with transaction.atomic():

            lsa = (
                LSAProfile.objects
                .select_for_update()
                .get(
                    pk=serializer.validated_data["lsa"].pk
                )
            )

            booking_data = serializer.validated_data.copy()
            booking_data["lsa"] = lsa

            overlapping = Booking.objects.filter(
                lsa=lsa,
                booking_date=booking_data["booking_date"],
                status__in=Booking.BLOCKING_STATUSES,
                start_time__lt=booking_data["end_time"],
                end_time__gt=booking_data["start_time"],
            )

            if overlapping.exists():
                return Response(
                    {
                        "booking": [
                            "This LSA already has a booking "
                            "during the selected time."
                        ]
                    },
                    status=status.HTTP_409_CONFLICT,
                )

            booking = Booking.objects.create(
                **booking_data
            )
        return Response(
            {
                "message": "Booking created successfully!",
                "data": BookingSerializer(booking).data,
            },
            status=status.HTTP_201_CREATED,
        )