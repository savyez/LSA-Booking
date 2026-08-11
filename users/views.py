from datetime import datetime, timedelta
from bookings.models import Booking
from .models import LSAProfile
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView, Response
from .serializers import ParentSerializer, LSAProfileSerializer

class ParentView(APIView):

    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = ParentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                    "message": "Parent Profile created successfully!",
                    "data": serializer.data,
                    },
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class LSAProfileView(APIView):

    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = LSAProfileSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "message": "LSA Profile created successfully!",
                    "data": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )


class LSASearchView(APIView):

    permission_classes = [AllowAny]

    def get(self, request):
        skill = request.query_params.get("skill")
        booking_date = request.query_params.get("booking_date")
        start_time = request.query_params.get("start_time")
        end_time = request.query_params.get("end_time")

        queryset = LSAProfile.objects.filter(is_active=True).prefetch_related("skills")
        if skill:
            queryset = queryset.filter(
                skills__name__iexact=skill.strip()
            ).distinct()

        if booking_date and start_time and end_time:
            try:
                b_date = datetime.strptime(booking_date, "%Y-%m-%d").date()
                s_time = datetime.strptime(start_time, "%H:%M:%S" if len(start_time) == 8 else "%H:%M").time()
                e_time = datetime.strptime(end_time, "%H:%M:%S" if len(end_time) == 8 else "%H:%M").time()

                req_start_dt = datetime.combine(b_date, s_time)
                req_end_dt = datetime.combine(b_date, e_time)
                if e_time <= s_time:
                    req_end_dt += timedelta(days=1)

                candidates = Booking.objects.filter(
                    booking_date__range=[b_date - timedelta(days=1), b_date + timedelta(days=1)],
                    status__in=Booking.BLOCKING_STATUSES,
                )

                conflicting_lsa_ids = set()
                for b in candidates:
                    b_start = datetime.combine(b.booking_date, b.start_time)
                    b_end = datetime.combine(b.booking_date, b.end_time)
                    if b.end_time <= b.start_time:
                        b_end += timedelta(days=1)
                    if b_start < req_end_dt and b_end > req_start_dt:
                        conflicting_lsa_ids.add(b.lsa_id)

                queryset = queryset.exclude(id__in=conflicting_lsa_ids)
            except ValueError:
                pass

        count = queryset.count()
        serializer = LSAProfileSerializer(
            queryset,
            many=True
        )

        return Response({
            "message": f"Found {count} LSAs!",
            "data": serializer.data,
        }, status=status.HTTP_200_OK)