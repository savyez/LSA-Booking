from decimal import Decimal
from django.db import models
import uuid


# Parent model for handling parent profiles
class Parent(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True, db_index=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Parent"
        verbose_name_plural = "Parents"

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


# LSA Profile model for handling LSA profiles
class LSAProfile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True, db_index=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    skills = models.TextField( blank=True, help_text="Comma-separated list of skills" )
    hourly_rate = models.DecimalField( max_digits=10, decimal_places=2, default=Decimal("0.00"))
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "LSA Profile"
        verbose_name_plural = "LSA Profiles"

        indexes = [
            models.Index(fields=["email"]),
            models.Index(fields=["is_active"]),
        ]

    def __str__(self):
        return f"{self.first_name} {self.last_name}"