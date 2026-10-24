from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from utils.enums import UserRole
from apps.departments.models import Department

User = get_user_model()


class DepartmentApiTests(APITestCase):
    def setUp(self):
        self.dept_road = Department.objects.create(
            name="Roads & Transport Department",
            code="ROAD",
            contact_email="roads@cirp.gov.et",
            responsible_asset_types=["road"]
        )
        self.dept_water = Department.objects.create(
            name="Water & Sanitation Department",
            code="WATER",
            contact_email="water@cirp.gov.et",
            responsible_asset_types=["water_point"]
        )

        self.system_admin = User.objects.create_user(
            email="sysadmin@cirp.gov.et",
            password="Password123!",
            role=UserRole.SYSTEM_ADMIN,
            is_staff=True,
            is_superuser=True
        )

        self.road_admin = User.objects.create_user(
            email="roadadmin@cirp.gov.et",
            password="Password123!",
            role=UserRole.DEPARTMENT_ADMIN,
            department=self.dept_road
        )

        self.citizen = User.objects.create_user(
            email="citizen@cirp.gov.et",
            password="Password123!",
            role=UserRole.CITIZEN
        )

    def test_list_departments_contains_react_kpi_fields(self):
        url = "/departments/"
        response = self.client.get(url, HTTP_USER_AGENT="Mozilla/5.0")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        res_data = response.json()
        self.assertIsInstance(res_data, list)
        self.assertEqual(len(res_data), 2)
        dept = res_data[0]

        # Verify React DepartmentRecordSchema required fields
        expected_fields = [
            "id", "name", "code", "responsible_asset_types",
            "total_assets", "active_reports", "active_tasks",
            "resolution_rate_percent", "avg_acceptance_hours", "avg_completion_days"
        ]
        for field in expected_fields:
            self.assertIn(field, dept, f"Field '{field}' missing from department response")

    def test_road_admin_can_update_own_department(self):
        self.client.force_authenticate(user=self.road_admin)
        url = f"/api/v1/departments/{self.dept_road.id}/"
        response = self.client.patch(url, {"contact_phone": "+251999999999"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.dept_road.refresh_from_db()
        self.assertEqual(self.dept_road.contact_phone, "+251999999999")

    def test_road_admin_forbidden_from_updating_other_department(self):
        self.client.force_authenticate(user=self.road_admin)
        url = f"/api/v1/departments/{self.dept_water.id}/"
        response = self.client.patch(url, {"contact_phone": "+251888888888"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_citizen_forbidden_from_updating_department(self):
        self.client.force_authenticate(user=self.citizen)
        url = f"/api/v1/departments/{self.dept_road.id}/"
        response = self.client.patch(url, {"contact_phone": "+251777777777"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
