import logging
from urllib.parse import urlparse
import requests
from django.conf import settings
from django.urls import resolve, Resolver404
from rest_framework import status as drf_status
from rest_framework.test import APIRequestFactory


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

    parsed = urlparse(gateway_url)
    is_local = (
        not parsed.netloc or
        parsed.hostname in ("127.0.0.1", "localhost", "testserver")
    )

    if is_local:
        try:
            match = resolve(parsed.path)
            factory = APIRequestFactory()
            request = factory.post(parsed.path, payload, format="json")
            response = match.func(request, *match.args, **match.kwargs)
            if drf_status.is_success(response.status_code):
                return response.data
            else:
                raise PaymentGatewayError(
                    f"Payment gateway returned status {response.status_code}."
                )
        except Resolver404:
            pass
        except PaymentGatewayError:
            raise
        except Exception as exc:
            logger.exception(
                "Internal payment gateway call failed for payment %s.",
                payment.id,
            )
            raise PaymentGatewayError(
                "Payment gateway request failed."
            ) from exc

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