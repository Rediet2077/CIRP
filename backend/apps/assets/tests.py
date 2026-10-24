from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from utils.enums import UserRole, AssetStatus, AssetCondition
from apps.departments.models import Department
from apps.assets.models import Asset, AssetType

User = get_user_model()


class AssetApiTests(APITestCase):
    def setUp(self):
        self.dept = Department.objects.create(
            name="Electricity & Lighting Department",
            code="ELEC",
            contact_email="lighting@cirp.gov.et"
        )

        self.asset_type = AssetType.objects.create(
            id="street_light",
            name="Street Lighting",
            responsible_department=self.dept,
            requires_location=True,
            is_active=True
        )

        self.dept_admin = User.objects.create_user(
            email="lightadmin@cirp.gov.et",
            password="Password123!",
            first_name="Aster",
            last_name="Desta",
            role=UserRole.DEPARTMENT_ADMIN,
            department=self.dept
        )

        self.citizen = User.objects.create_user(
            email="citizen@cirp.gov.et",
            password="Password123!",
            role=UserRole.CITIZEN
        )

        self.existing_asset = Asset.objects.create(
            asset_code="AST-SL-BOL-001",
            name="Street Light Pole 001",
            asset_type=self.asset_type,
            department=self.dept,
            status=AssetStatus.ACTIVE,
            condition=AssetCondition.GOOD,
            latitude=9.0192,
            longitude=38.7525,
            address="Bole Medhanialem Avenue",
            registered_by=self.dept_admin,
            specific_data={"sl_pole_type": "Steel", "sl_wattage": "150W"}
        )

    def test_get_asset_types(self):
        url = "/api/v1/asset-types/"
        response = self.client.get(url, HTTP_USER_AGENT="Mozilla/5.0")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        res_data = response.json()
        self.assertIsInstance(res_data, list)
        self.assertTrue(len(res_data) >= 1)
        item = res_data[0]
        self.assertIn("id", item)
        self.assertIn("name", item)
        self.assertIn("responsible_department_id", item)
        self.assertIn("category_id", item)
        self.assertIn("total_assets_count", item)

    def test_list_assets_matches_react_schema(self):
        url = "/api/v1/assets/"
        response = self.client.get(url, HTTP_USER_AGENT="Mozilla/5.0")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        res_data = response.json()
        self.assertIsInstance(res_data, list)
        self.assertEqual(len(res_data), 1)

        asset = res_data[0]
        expected_keys = [
            "id", "asset_code", "asset_type_id", "asset_type_label",
            "department_id", "department_name", "status", "condition",
            "latitude", "longitude", "address", "registered_by",
            "active_reports_count", "specific_data"
        ]
        for key in expected_keys:
            self.assertIn(key, asset, f"Key '{key}' missing from asset response")

        self.assertEqual(asset["latitude"], 9.0192)
        self.assertEqual(asset["longitude"], 38.7525)
        self.assertEqual(asset["specific_data"]["sl_wattage"], "150W")

    def test_register_asset_requires_admin_permissions(self):
        url = "/api/v1/assets/"
        payload = {
            "asset_code": "AST-SL-BOL-002",
            "asset_type_id": "street_light",
            "department_id": str(self.dept.id),
            "name": "Street Light Pole 002",
            "status": "ACTIVE",
            "condition": "EXCELLENT",
            "latitude": 9.0200,
            "longitude": 38.7530,
            "address": "Bole Road",
        }

        # 1. Unauthenticated -> 401
        res_anon = self.client.post(url, payload, format='json')
        self.assertEqual(res_anon.status_code, status.HTTP_401_UNAUTHORIZED)

        # 2. Ordinary citizen -> 403
        self.client.force_authenticate(user=self.citizen)
        res_cit = self.client.post(url, payload, format='json')
        self.assertEqual(res_cit.status_code, status.HTTP_403_FORBIDDEN)

        # 3. Department Admin -> 201 Created
        self.client.force_authenticate(user=self.dept_admin)
        res_admin = self.client.post(url, payload, format='json')
        self.assertEqual(res_admin.status_code, status.HTTP_201_CREATED)

        created_asset = res_admin.json()
        self.assertEqual(created_asset["asset_code"], "AST-SL-BOL-002")
        self.assertEqual(created_asset["condition"], "EXCELLENT")

    def test_register_asset_invalid_coordinates(self):
        self.client.force_authenticate(user=self.dept_admin)
        url = "/api/v1/assets/"

        # Invalid latitude (> 90.0)
        invalid_payload = {
            "asset_code": "AST-SL-ERR-001",
            "asset_type_id": "street_light",
            "department_id": str(self.dept.id),
            "name": "Out of bounds asset",
            "status": "ACTIVE",
            "condition": "GOOD",
            "latitude": 125.0, # Illegal latitude
            "longitude": 38.7500,
            "address": "Invalid coordinate test",
        }
        response = self.client.post(url, invalid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_asset_duplicate_code(self):
        self.client.force_authenticate(user=self.dept_admin)
        url = "/api/v1/assets/"

        duplicate_payload = {
            "asset_code": "AST-SL-BOL-001", # Already exists
            "asset_type_id": "street_light",
            "department_id": str(self.dept.id),
            "name": "Duplicate Code Asset",
            "status": "ACTIVE",
            "condition": "GOOD",
            "latitude": 9.0192,
            "longitude": 38.7525,
            "address": "Same address",
        }
        response = self.client.post(url, duplicate_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
