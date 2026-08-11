from bookings.models import Booking
from decimal import Decimal
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from users.models import Parent, LSAProfile


class LSASearchAPITests(APITestCase):

    def setUp(self):
        self.url = reverse("LSA-search")
        self.active_lsa = LSAProfile.objects.create(
            first_name="Bob",
            last_name="Marley",
            email="bob.marley@example.com",
            skills="Autism, ADHD, English",
            hourly_rate=Decimal("700.00"),
            is_active=True,
        )
        self.inactive_lsa = LSAProfile.objects.create(
            first_name="Rupam",
            last_name="Islam",
            email="rupam.islam@example.com",
            skills="Autism, singing",
            hourly_rate=Decimal("650.00"),
            is_active=False,
        )

    def test_lsa_search_skill_and_availability(self):
        parent = Parent.objects.create(
            first_name="Jane",
            last_name="Doe",
            email="jane@example.com",
        )
        Booking.objects.create(
            parent=parent,
            lsa=self.active_lsa,
            booking_date="2026-08-15",
            start_time="10:00",
            end_time="12:00",
            status=Booking.Status.CONFIRMED,
        )
        alice = LSAProfile.objects.create(
            first_name="Alice",
            last_name="Smith",
            email="alice@example.com",
            skills="ADHD",
            hourly_rate=Decimal("600.00"),
            is_active=True,
        )

        response = self.client.get(
            f"{self.url}?skill=adhd&booking_date=2026-08-15&start_time=11:00&end_time=13:00"
        )
        self.assertEqual(
            response.status_code, 
            status.HTTP_200_OK
            )
        self.assertEqual(
            len(response.data["data"]), 
            1
            )
        self.assertEqual(
            response.data["data"][0]["first_name"], 
            "Alice"
            )
