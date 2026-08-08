from .models import Payment
from rest_framework.serializers import ModelSerializer


class PaymentSerializer(ModelSerializer):

    class Meta:
        model=Payment
        fields=[
            'id',
            'transaction_id',
            'amount',
            'status',
            'created_at',
            'updated_at',
            'booking',
        ]
        read_only_fields=[
            "id",
            "transaction_id",
            "status",
            "created_at",
            "updated_at",
        ]