from django.urls import path
from .views import PaymentView, MockPaymentGatewayView, PaymentWebhookView

urlpatterns = [
    path('payments/', PaymentView.as_view(), name="payment-view"),
    path('payments/mock-gateway/', MockPaymentGatewayView.as_view() , name="payment-gateway"),
    path('payments/webhook/', PaymentWebhookView.as_view() , name="payment-webhook"),
]