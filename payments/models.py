from django.db import models
from bookings.models import Booking
import uuid

# Payment model for handling payments for bookings
class Payment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        SUCCESS = "SUCCESS", "Success"
        FAILED = "FAILED", "Failed"

    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name="payment")
    transaction_id = models.CharField(max_length=100, unique=True, blank=True, null=True, editable=False)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Payment"
        verbose_name_plural = "Payments"

    def __str__(self):
        return (
            f"Payment #{self.id} "
            f"({self.status})"
        )