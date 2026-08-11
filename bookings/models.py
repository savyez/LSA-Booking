from datetime import datetime
from decimal import Decimal
from django.core.exceptions import ValidationError
from django.db import models
import uuid
from users.models import Parent, LSAProfile


class Booking(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        CONFIRMED = "CONFIRMED", "Confirmed"
        CANCELLED = "CANCELLED", "Cancelled"
        PAYMENT_FAILED = "PAYMENT_FAILED", "Payment Failed"

    """ Statuses that actually hold the LSA's calendar slot. A cancelled
     or payment-failed booking frees the slot back up for rebooking."""
    BLOCKING_STATUSES = (Status.PENDING, Status.CONFIRMED)

    parent = models.ForeignKey(Parent, on_delete=models.CASCADE, related_name="bookings")
    lsa = models.ForeignKey(LSAProfile, on_delete=models.CASCADE, related_name="bookings")
    booking_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-booking_date", "-start_time"]
        indexes = [
            models.Index(fields=["booking_date"]),
            models.Index(fields=["status"]),
            models.Index(fields=["lsa", "booking_date"]),
        ]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(end_time__gt=models.F("start_time")),
                name="booking_end_after_start",
            )
        ]

    def clean(self):
        """Validates time ordering and rejects overlapping bookings
        for the same LSA on the same date.

        This is the app-level enforcement of the brief's "built-in
        validation preventing overlapping sessions" requirement. It
        runs on every save() below, so it can't be skipped by a
        caller forgetting to call full_clean() manually. A real
        DB-level guarantee (Postgres EXCLUDE constraint) belongs in
        a later migration once this app targets Postgres in prod —
        this validator is the portable fallback that also works on
        SQLite for local dev/tests.
        """
        super().clean()

        if self.start_time and self.end_time and self.start_time >= self.end_time:
            raise ValidationError("End time must be after start time.")

        if not (self.lsa_id and self.booking_date and self.start_time and self.end_time):
            return

        overlapping = self.__class__.objects.filter(
            lsa_id=self.lsa_id,
            booking_date=self.booking_date,
            status__in=self.BLOCKING_STATUSES,
            start_time__lt=self.end_time,
            end_time__gt=self.start_time,
        ).exclude(pk=self.pk)

        if overlapping.exists():
            raise ValidationError(
                {
                    "__all__": (
                        "This LSA already has a booking during the selected time."
                    )
                }
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def duration_hours(self):
        if not (self.booking_date and self.start_time and self.end_time):
            return Decimal("0.00")
        start_dt = datetime.combine(self.booking_date, self.start_time)
        end_dt = datetime.combine(self.booking_date, self.end_time)
        seconds = (end_dt - start_dt).total_seconds()
        return Decimal(str(seconds / 3600))

    @property
    def total_amount(self):
        if not hasattr(self, "lsa") or self.lsa is None:
            return Decimal("0.00")
        return (self.lsa.hourly_rate * self.duration_hours).quantize(Decimal("0.01"))

    def __str__(self):
        return (
            f"{self.parent} → "
            f"{self.lsa} "
            f"({self.booking_date})"
        )