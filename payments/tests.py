from decimal import Decimal
from unittest.mock import patch
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from bookings.models import Booking
from payments.models import Payment
from users.models import Parent, LSAProfile


class PaymentAPITestCase(APITestCase):

    def setUp(self):
        self.payment_url = reverse("payment-view")
        self.webhook_url = reverse("payment-webhook")

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
        self.booking = Booking.objects.create(
            parent=self.parent,
            lsa=self.lsa,
            booking_date="2026-08-09",
            start_time="21:00",
            end_time="22:00",
        )

    @patch("payments.views.process_payment")
    def test_initiate_payment_success(self, mock_process_payment):
        mock_process_payment.return_value = {
            "transaction_id": "tx_12345",
            "status": "SUCCESS",
        }
        payload = {
            "booking": str(self.booking.id)
            }
        response = self.client.post(
            self.payment_url, 
            data=payload, 
            format="json"
            )

        self.assertEqual(
            response.status_code, 
            status.HTTP_201_CREATED
            )
        self.assertEqual(
            Payment.objects.count(), 
            1
            )
        payment = Payment.objects.get(
            booking=self.booking
            )
        self.assertEqual(
            payment.amount, 
            Decimal("650.00")
            )
        self.assertEqual(
            payment.status, 
            Payment.Status.PENDING
            )

    def test_initiate_payment_duplicate_conflict(self):
        Payment.objects.create(
            booking=self.booking,
            amount=self.lsa.hourly_rate,
        )
        payload = {
            "booking": str(self.booking.id)
            }
        response = self.client.post(
            self.payment_url, 
            data=payload, 
            format="json"
            )

        self.assertEqual(
            response.status_code, 
            status.HTTP_409_CONFLICT
            )

    def test_webhook_payment_success_confirms_booking(self):
        payment = Payment.objects.create(
            booking=self.booking,
            amount=self.lsa.hourly_rate,
        )
        payload = {
            "payment_id": str(payment.id),
            "transaction_id": "tx_99999",
            "status": Payment.Status.SUCCESS,
        }
        response = self.client.post(
            self.webhook_url, 
            data=payload, 
            format="json"
            )

        self.assertEqual(
            response.status_code, 
            status.HTTP_200_OK
            )
        payment.refresh_from_db()
        self.booking.refresh_from_db()

        self.assertEqual(
            payment.status, 
            Payment.Status.SUCCESS
            )
        self.assertEqual(
            payment.transaction_id, 
            "tx_99999"
            )
        self.assertEqual(
            self.booking.status, 
            Booking.Status.CONFIRMED
            )

    def test_webhook_payment_failed_updates_booking(self):
        payment = Payment.objects.create(
            booking=self.booking,
            amount=self.lsa.hourly_rate,
        )
        payload = {
            "payment_id": str(payment.id),
            "transaction_id": "tx_88888",
            "status": Payment.Status.FAILED,
        }
        response = self.client.post(
            self.webhook_url, 
        data=payload, 
        format="json"
        )

        self.assertEqual(
            response.status_code, 
        status.HTTP_200_OK
        )
        payment.refresh_from_db()
        self.booking.refresh_from_db()

        self.assertEqual(
            payment.status, 
        Payment.Status.FAILED
        )
        self.assertEqual(
            self.booking.status, 
        Booking.Status.PAYMENT_FAILED
        )
