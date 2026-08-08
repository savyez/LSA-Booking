from rest_framework import serializers
from .models import Parent, LSAProfile


class ParentSerializer(serializers.ModelSerializer):


    class Meta:
        model = Parent
        fields = [
            "id",
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
        ]

class LSAProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = LSAProfile
        fields = [
            "id",
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "skills",
            "hourly_rate",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
        ]