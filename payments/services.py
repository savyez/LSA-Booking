import logging
import requests
from django.conf import settings


logger = logging.getLogger(__name__)


class PaymentGatewayError(Exception):
    """Raised when the payment gateway request fails."""
    pass


def process_payment(payment):

    payload = {
        "payment_id": str(payment.id),
        "amount": str(payment.amount),
    }

    gateway_url = getattr(
        settings,
        "PAYMENT_GATEWAY_URL",
        "http://127.0.0.1:8000/api/v1/payments/mock-gateway/",
    )

    try:
        response = requests.post(
            gateway_url,
            json=payload,
            timeout=5,
        )

        response.raise_for_status()

    except requests.Timeout as exc:
        logger.exception(
            "Payment gateway timed out for payment %s.",
            payment.id,
        )

        raise PaymentGatewayError(
            "Payment gateway request timed out."
        ) from exc

    except requests.RequestException as exc:
        logger.exception(
            "Payment gateway request failed for payment %s.",
            payment.id,
        )

        raise PaymentGatewayError(
            "Payment gateway request failed."
        ) from exc

    try:
        return response.json()

    except ValueError as exc:
        logger.exception(
            "Payment gateway returned invalid JSON for payment %s.",
            payment.id,
        )

        raise PaymentGatewayError(
            "Payment gateway returned an invalid response."
        ) from exc