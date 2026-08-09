from decimal import Decimal
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from users.models import Parent, LSAProfile


class ParentAPITests(APITestCase):

    def setUp(self):
        self.url = reverse("parent-view")

    def test_create_parent(self):
        payload = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "john@example.com",
            "phone_number": "9876543210",
        }
        response = self.client.post(
            self.url, 
            data=payload, 
            format="json"
            )
        self.assertEqual(
            response.status_code, 
            status.HTTP_201_CREATED
            )
        self.assertEqual(
            Parent.objects.count(), 
            1
            )
        self.assertEqual(
            response.data["data"]["email"], 
            "john@example.com"
            )

    def test_duplicate_parent_email(self):
        Parent.objects.create(
            first_name="John",
            last_name="Doe",
            email="john@example.com",
        )
        payload = {
            "first_name": "Jane",
            "last_name": "Doe",
            "email": "john@example.com",
        }
        response = self.client.post(
            self.url, 
            data=payload, 
            format="json"
            )
        self.assertEqual(
            response.status_code, 
            status.HTTP_400_BAD_REQUEST
            )


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

    def test_lsa_skill_search(self):
        response = self.client.get(
            f"{self.url}?skill=adhd"
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

    def test_lsa_search_active_only(self):
        response = self.client.get(self.url)
        self.assertEqual(
            response.status_code, 
            status.HTTP_200_OK
            )
        self.assertEqual(
            len(response.data["data"]), 
            1
            )
        self.assertEqual(
            response.data["data"][0]["email"], 
            "bob.marley@example.com"
            )
