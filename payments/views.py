import uuid
from .models import Payment
from django.db import IntegrityError, transaction
from rest_framework import status
from bookings.models import Booking
from rest_framework.views import APIView
from .serializers import PaymentSerializer
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .services import PaymentGatewayError, process_payment


class PaymentView(APIView):

    permission_classes = [AllowAny]

    def post(self, request):

        booking_id = request.data.get("booking")
        if not booking_id:
            return Response(
                {
                    "booking": [
                        "Booking is required."
                    ]
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            with transaction.atomic():

                booking = (
                    Booking.objects
                    .select_for_update()
                    .select_related("lsa")
                    .get(pk=booking_id)
                )

                if hasattr(booking, "payment"):
                    return Response(
                        {
                            "payment": [
                                "A payment already exists "
                                "for this booking."
                            ]
                        },
                        status=status.HTTP_409_CONFLICT,
                    )
                payment = Payment.objects.create(
                    booking=booking,
                    amount=booking.total_amount,
                )
                gateway_response = process_payment(payment)
        except Booking.DoesNotExist:
            return Response(
                {
                    "booking": [
                        "Booking does not exist."
                    ]
                },
                status=status.HTTP_404_NOT_FOUND,
            )
        except PaymentGatewayError:
            return Response(
                {
                    "message": "Payment gateway is currently unavailable."
                },
                status=status.HTTP_502_BAD_GATEWAY,
            )

        return Response(
            {
                "message": "Payment initiated successfully!",
                "data": PaymentSerializer(payment).data,
                "gateway_response": gateway_response,
            },
            status=status.HTTP_201_CREATED,
        )

class MockPaymentGatewayView(APIView):

    permission_classes = [AllowAny]

    def post(self, request):
        payment_id = request.data.get("payment_id")
        amount = request.data.get("amount")
        simulate_status = request.data.get(
            "simulate_status",
            Payment.Status.SUCCESS,
        )

        if not payment_id:
            return Response(
                {
                    "payment_id": [
                        "Payment ID is required."
                    ]
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not amount:
            return Response(
                {
                    "amount": [
                        "Amount is required."
                    ]
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        if simulate_status not in [
            Payment.Status.SUCCESS,
            Payment.Status.FAILED,
        ]:
            return Response(
                {
                    "status": [
                        "Status must be SUCCESS or FAILED."
                    ]
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        transaction_id = str(uuid.uuid4())
        return Response(
            {
                "transaction_id": transaction_id,
                "status": simulate_status,
            },
            status=status.HTTP_200_OK,
        )

class PaymentWebhookView(APIView):

    permission_classes = [AllowAny]

    def post(self, request):
        payment_id = request.data.get("payment_id")
        transaction_id = request.data.get("transaction_id")
        payment_status = request.data.get("status")
        if not payment_id:
            return Response(
                {
                    "payment_id": [
                        "Payment ID is required."
                    ]
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not transaction_id:
            return Response(
                {
                    "transaction_id": [
                        "Transaction ID is required."
                    ]
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        if payment_status not in [
            Payment.Status.SUCCESS,
            Payment.Status.FAILED,
        ]:
            return Response(
                {
                    "status": [
                        "Payment status must be SUCCESS or FAILED."
                    ]
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        try:
            with transaction.atomic():

                payment = (
                    Payment.objects
                    .select_for_update()
                    .select_related("booking")
                    .get(pk=payment_id)
                )
                if payment.status != Payment.Status.PENDING:            # Ignore duplicate webhook notifications.
                    return Response(
                        {
                            "message": "Payment has already been processed."
                        },
                        status=status.HTTP_200_OK,
                    )

                if Payment.objects.filter(transaction_id=transaction_id).exclude(pk=payment_id).exists():
                    return Response(
                        {
                            "transaction_id": [
                                "A payment with this transaction ID already exists."
                            ]
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                payment.transaction_id = transaction_id
                payment.status = payment_status

                payment.save(
                    update_fields=[
                        "transaction_id",
                        "status",
                        "updated_at",
                    ]
                )
                booking = payment.booking
                if payment_status == Payment.Status.SUCCESS:
                    booking.status = Booking.Status.CONFIRMED
                else:
                    booking.status = Booking.Status.PAYMENT_FAILED
                booking.save(
                    update_fields=[
                        "status",
                        "updated_at",
                    ]
                )
        except Payment.DoesNotExist:
            return Response(
                {
                    "payment_id": [
                        "Payment does not exist."
                    ]
                },
                status=status.HTTP_404_NOT_FOUND,
            )
        except IntegrityError:
            return Response(
                {
                    "transaction_id": [
                        "A payment with this transaction ID already exists."
                    ]
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        return Response(
            {
                "message": "Payment webhook processed successfully.",
                "payment_status": payment.status,
                "booking_status": booking.status,
            },
            status=status.HTTP_200_OK,
        )