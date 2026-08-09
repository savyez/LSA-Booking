from decimal import Decimal
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from bookings.models import Booking
from users.models import Parent, LSAProfile


class BookingAPITestCase(APITestCase):

    def setUp(self):
        self.url = reverse("booking-create")
        self.parent = Parent.objects.create(
            first_name="John",
            last_name="Doe",
            email="john@example.com",
        )
        self.lsa = LSAProfile.objects.create(
            first_name="Alice",
            last_name="Smith",
            email="alice@example.com",
            skills="Autism, ADHD",
            hourly_rate=Decimal("650.00"),
            is_active=True,
        )

    def test_create_booking_success(self):
        payload = {
            "parent": str(self.parent.id),
            "lsa": str(self.lsa.id),
            "booking_date": "2026-08-09",
            "start_time": "21:00",
            "end_time": "22:00",
        }
        response = self.client.post(
            self.url, 
            data=payload, 
            format="json"
            )
        self.assertEqual(
            response.status_code, 
            status.HTTP_201_CREATED
            )
        self.assertEqual(
            Booking.objects.count(), 
            1
            )
        self.assertEqual(
            response.data["message"], 
            "Booking created successfully!"
            )

    def test_create_overlapping_booking(self):
        payload = {
            "parent": str(self.parent.id),
            "lsa": str(self.lsa.id),
            "booking_date": "2026-08-09",
            "start_time": "21:00",
            "end_time": "22:00",
        }

        first_response = self.client.post(                 # First booking succeeds
            self.url, 
            data=payload, 
            format="json"
            )
        self.assertEqual(
            first_response.status_code, 
            status.HTTP_201_CREATED
            )

        second_response = self.client.post(                # Overlapping booking fails with 409 CONFLICT
            self.url, 
            data=payload, 
            format="json"
            )
        self.assertEqual(
            second_response.status_code, 
            status.HTTP_409_CONFLICT
            )
        self.assertEqual(
            Booking.objects.count(), 
            1
            )

    def test_create_booking_invalid_time_range(self):
        payload = {
            "parent": str(self.parent.id),
            "lsa": str(self.lsa.id),
            "booking_date": "2026-08-09",
            "start_time": "22:00",
            "end_time": "21:00",
        }
        response = self.client.post(
            self.url, 
            data=payload, 
            format="json"
            )
        self.assertEqual(
            response.status_code, 
            status.HTTP_400_BAD_REQUEST
            )
        self.assertIn(
            "end_time", 
            response.data
            )

    def test_create_booking_missing_required_fields(self):
        payload = {
            "booking_date": "2026-08-09",
            "start_time": "21:00",
            "end_time": "22:00",
        }
        response = self.client.post(
            self.url, 
            data=payload, 
            format="json"
            )
        self.assertEqual(
            response.status_code, 
            status.HTTP_400_BAD_REQUEST
            )
        self.assertIn(
            "parent", 
            response.data
            )
        self.assertIn(
            "lsa", 
            response.data
            )