from rest_framework.test import APITestCase
from rest_framework import status
from apps.departments.models import Department
from apps.categories.models import Category


class CategoryApiTests(APITestCase):
    def setUp(self):
        self.dept = Department.objects.create(
            name="Roads & Transport",
            code="ROAD",
            contact_email="roads@cirp.gov.et"
        )
        self.cat1 = Category.objects.create(
            name="Road Damage",
            code="road_damage",
            icon="🛣️",
            default_department=self.dept,
            is_active=True
        )
        self.cat2 = Category.objects.create(
            name="Water Leakage",
            code="water_leakage",
            icon="💧",
            is_active=True
        )

    def test_get_categories_flutter_envelope(self):
        url = "/api/v1/categories/"
        response = self.client.get(url, HTTP_USER_AGENT="Dart/3.4 (dart:io)")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        res_data = response.json()
        self.assertTrue(res_data.get('success'))
        self.assertIn('data', res_data)
        self.assertEqual(len(res_data['data']), 2)
        codes = [c['code'] for c in res_data['data']]
        self.assertIn('road_damage', codes)
        self.assertIn('water_leakage', codes)

    def test_get_categories_react_direct_array(self):
        url = "/categories/"
        response = self.client.get(url, HTTP_USER_AGENT="Mozilla/5.0")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        res_data = response.json()
        self.assertIsInstance(res_data, list)
        self.assertEqual(len(res_data), 2)
        first = res_data[0]
        self.assertIn('name', first)
        self.assertIn('code', first)
        self.assertIn('icon', first)

    def test_search_categories(self):
        url = "/api/v1/categories/?search=water"
        response = self.client.get(url, HTTP_USER_AGENT="Mozilla/5.0")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        res_data = response.json()
        self.assertEqual(len(res_data), 1)
        self.assertEqual(res_data[0]['code'], 'water_leakage')
