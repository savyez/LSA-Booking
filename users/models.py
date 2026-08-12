from decimal import Decimal
from django.db import models
import uuid


# Parent model for handling parent profiles
class Parent(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True, db_index=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Parent"
        verbose_name_plural = "Parents"

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Skill(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Skill"
        verbose_name_plural = "Skills"

    def __str__(self):
        return self.name


class LSAProfileManager(models.Manager):
    def create(self, **kwargs):
        skills_raw = kwargs.pop("skills", None)
        instance = super().create(**kwargs)
        if skills_raw is not None:
            instance.set_skills(skills_raw)
        return instance


# LSA Profile model for handling LSA profiles
class LSAProfile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True, db_index=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    skills = models.ManyToManyField(Skill, related_name="lsa_profiles", blank=True)
    hourly_rate = models.DecimalField( max_digits=10, decimal_places=2, default=Decimal("0.00"))
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = LSAProfileManager()

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "LSA Profile"
        verbose_name_plural = "LSA Profiles"

        indexes = [
            models.Index(fields=["email"]),
            models.Index(fields=["is_active"]),
        ]

    def set_skills(self, skills_raw):
        if isinstance(skills_raw, str):
            names = [s.strip() for s in skills_raw.split(",") if s.strip()]
        elif isinstance(skills_raw, (list, set, tuple)):
            names = [str(s).strip() for s in skills_raw if str(s).strip()]
        else:
            names = []
        if not names:
            self.skills.clear()
            return

        unique_names = list(dict.fromkeys(names))
        existing = {s.name: s for s in Skill.objects.filter(name__in=unique_names)}
        missing_names = [n for n in unique_names if n not in existing]

        if missing_names:
            Skill.objects.bulk_create([Skill(name=n) for n in missing_names], ignore_conflicts=True)
            skills = list(Skill.objects.filter(name__in=unique_names))
        else:
            skills = list(existing.values())

        self.skills.set(skills)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"