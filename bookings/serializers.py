from django.utils import timezone
from .models import Booking
from rest_framework.serializers import ModelSerializer
from rest_framework.serializers import ValidationError as rest_validation_error


class BookingSerializer(ModelSerializer):
    class Meta:
        model = Booking
        fields = [
            'id',
            'parent',
            'lsa',
            'booking_date',
            'start_time',
            'end_time',
            'status',
            'created_at',
            'updated_at',
        ]

        read_only_fields = [
            "id",
            "status",
            "created_at",
            "updated_at",
        ]

    def validate(self, data):
        parent = data.get("parent", getattr(self.instance, "parent", None))
        lsa = data.get("lsa", getattr(self.instance, "lsa", None))
        booking_date = data.get("booking_date", getattr(self.instance, "booking_date", None))
        start_time = data.get("start_time", getattr(self.instance, "start_time", None))
        end_time = data.get("end_time", getattr(self.instance, "end_time", None))

        if not parent:
            raise rest_validation_error(
                {"parent": "Parent is required."}
            )

        if not lsa:
            raise rest_validation_error(
                {"lsa": "LSA is required."}
            )

        if not lsa.is_active:
            raise rest_validation_error(
                {"lsa": ["Cannot book an inactive LSA profile."]}
            )

        if not booking_date:
            raise rest_validation_error(
                {"booking_date": "Booking date is required."}
            )

        if not start_time or not end_time:
            raise rest_validation_error(
                {"non_field_errors": ["Start time and end time are required."]}
            )

        if start_time == end_time:
            raise rest_validation_error(
                {"end_time": "Start time and end time cannot be equal."}
            )

        if booking_date and start_time:
            now = timezone.localtime()
            today = now.date()
            now_time = now.time()
            if booking_date < today or (booking_date == today and start_time < now_time):
                raise rest_validation_error(
                    {"booking_date": ["Booking date and time cannot be in the past."]}
                )
        
        return data