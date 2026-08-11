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
    skills = serializers.CharField(required=False, allow_blank=True)

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

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        skill_names = [skill.name for skill in instance.skills.all()]
        ret["skills"] = ", ".join(skill_names)
        return ret

    def create(self, validated_data):
        skills_raw = validated_data.pop("skills", None)
        profile = super().create(validated_data)
        if skills_raw is not None:
            profile.set_skills(skills_raw)
        return profile

    def update(self, instance, validated_data):
        skills_raw = validated_data.pop("skills", None)
        profile = super().update(instance, validated_data)
        if skills_raw is not None:
            profile.set_skills(skills_raw)
        return profile