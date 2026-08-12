from bookings.models import Booking
from decimal import Decimal
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from users.models import Parent, LSAProfile


class LSASearchAPITests(APITestCase):

    def setUp(self):
        self.url = reverse("LSA-search")
        self.active_lsa = LSAProfile.objects.create(
            first_name="Bob",
            last_name="Marley",
            email="bob.marley@example.com",
            skills="Autism, ADHD, English",
            hourly_rate=Decimal("700.00"),
            is_active=True,
        )
        self.inactive_lsa = LSAProfile.objects.create(
            first_name="Rupam",
            last_name="Islam",
            email="rupam.islam@example.com",
            skills="Autism, singing",
            hourly_rate=Decimal("650.00"),
            is_active=False,
        )

    def test_lsa_search_skill_and_availability(self):
        parent = Parent.objects.create(
            first_name="Jane",
            last_name="Doe",
            email="jane@example.com",
        )
        Booking.objects.create(
            parent=parent,
            lsa=self.active_lsa,
            booking_date="2026-08-15",
            start_time="10:00",
            end_time="12:00",
            status=Booking.Status.CONFIRMED,
        )
        alice = LSAProfile.objects.create(
            first_name="Alice",
            last_name="Smith",
            email="alice@example.com",
            skills="ADHD",
            hourly_rate=Decimal("600.00"),
            is_active=True,
        )

        response = self.client.get(
            f"{self.url}?skill=adhd&booking_date=2026-08-15&start_time=11:00&end_time=13:00"
        )
        self.assertEqual(
            response.status_code, 
            status.HTTP_200_OK
            )
        self.assertEqual(
            len(response.data["data"]), 
            1
            )
        self.assertEqual(
            response.data["data"][0]["first_name"], 
            "Alice"
            )

    def test_lsa_search_substring_skill(self):
        response = self.client.get(
            f"{self.url}?skill=adh"
        )
        self.assertEqual(
            response.status_code, 
        status.HTTP_200_OK
        )
        self.assertEqual(
            len(response.data["data"]), 
        1
        )
        self.assertEqual(
            response.data["data"][0]["first_name"], 
        "Bob"
        )

    def test_set_skills_n_plus_one_prevention(self):
        lsa = LSAProfile.objects.create(
            first_name="Skill",
            last_name="Tester",
            email="skill@example.com",
            hourly_rate=Decimal("500.00"),
        )
        # Adding 5 new skills in one set_skills call
        skills_input = "Skill1, Skill2, Skill3, Skill4, Skill5"
        with self.assertNumQueries(5):
            # 1: fetch existing skills, 2: bulk_create missing, 3: fetch all added skills, 4: check existing M2M, 5: bulk insert M2M
            lsa.set_skills(skills_input)
        self.assertEqual(lsa.skills.count(), 5)

    def test_lsa_search_prefetch_prevents_n_plus_one(self):
        # Create 5 LSA profiles
        for i in range(5):
            LSAProfile.objects.create(
                first_name=f"LSA_{i}",
                last_name="Test",
                email=f"lsa_{i}@example.com",
                skills=f"SkillA, SkillB, Skill_{i}",
                hourly_rate=Decimal("500.00"),
                is_active=True,
            )

        with self.assertNumQueries(3):
            # 1: COUNT(*) query, 2: LSAProfile list query, 3: prefetched skills (M2M) single query
            response = self.client.get(self.url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertGreaterEqual(len(response.data["data"]), 5)

