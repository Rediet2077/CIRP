from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from utils.enums import UserRole
from apps.departments.models import Department

User = get_user_model()


class AuthenticationAndUserTests(APITestCase):
    def setUp(self):
        # Create a test department
        self.dept = Department.objects.create(
            name="Roads & Transport Department",
            code="ROAD",
            contact_email="roads@cirp.gov.et"
        )

        # Create active System Admin
        self.system_admin = User.objects.create_user(
            email="admin@cirp.gov.et",
            password="AdminPassword123!",
            first_name="City",
            last_name="Admin",
            role=UserRole.SYSTEM_ADMIN,
            status=User.StatusChoices.ACTIVE,
            is_staff=True,
            is_superuser=True
        )

        # Create active Department Admin
        self.dept_admin = User.objects.create_user(
            email="roadadmin@cirp.gov.et",
            password="RoadPassword123!",
            first_name="Road",
            last_name="Admin",
            role=UserRole.DEPARTMENT_ADMIN,
            status=User.StatusChoices.ACTIVE,
            department=self.dept
        )

        # Create active Citizen
        self.citizen = User.objects.create_user(
            email="citizen@cirp.gov.et",
            password="CitizenPassword123!",
            first_name="Abebe",
            last_name="Bikila",
            phone_number="+251911223344",
            role=UserRole.CITIZEN,
            status=User.StatusChoices.ACTIVE
        )

    # -------------------------------------------------------------------------
    # 1. Citizen Registration Tests (Flutter)
    # -------------------------------------------------------------------------
    def test_citizen_registration_success(self):
        url = "/api/v1/auth/register/"
        data = {
            "email": "newcitizen@example.com",
            "phone_number": "+251922334455",
            "first_name": "New",
            "last_name": "Citizen",
            "password": "SecurePassword123!",
            "password_confirm": "SecurePassword123!",
            "preferred_language": "en"
        }
        # Simulate Flutter client headers
        response = self.client.post(url, data, format='json', HTTP_USER_AGENT="Dart/3.4 (dart:io)")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Verify Flutter response structure
        res_data = response.json()
        self.assertTrue(res_data.get('success'))
        self.assertIn('data', res_data)
        self.assertIn('user', res_data['data'])
        self.assertIn('tokens', res_data['data'])
        self.assertEqual(res_data['data']['user']['email'], "newcitizen@example.com")
        self.assertEqual(res_data['data']['user']['role'], UserRole.CITIZEN)

    def test_citizen_registration_mismatched_password(self):
        url = "/api/v1/auth/register/"
        data = {
            "email": "fail@example.com",
            "first_name": "Fail",
            "last_name": "User",
            "password": "Password123!",
            "password_confirm": "DifferentPassword123!",
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        res_data = response.json()
        self.assertFalse(res_data.get('success'))

    def test_citizen_registration_duplicate_email(self):
        url = "/api/v1/auth/register/"
        data = {
            "email": "citizen@cirp.gov.et", # Existing email
            "first_name": "Duplicate",
            "last_name": "User",
            "password": "Password123!",
            "password_confirm": "Password123!",
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # -------------------------------------------------------------------------
    # 2. Department Admin Application Tests (React Admin)
    # -------------------------------------------------------------------------
    def test_department_application_success(self):
        url = "/departments/apply/"
        data = {
            "department_name": "Sanitation & Greenery",
            "department_code": "GREEN",
            "department_email": "green@cirp.gov.et",
            "department_phone": "+251111999999",
            "address": "Bole Subcity, Addis Ababa",
            "representative_first_name": "Marta",
            "representative_last_name": "Alemu",
            "representative_email": "marta.alemu@cirp.gov.et",
            "representative_phone": "+251933445566",
            "password": "SecurePassword123!"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        res_data = response.json()
        self.assertIn("message", res_data)

        # Verify that department and user were created with PENDING status and inactive
        applicant = User.objects.get(email="marta.alemu@cirp.gov.et")
        self.assertEqual(applicant.status, User.StatusChoices.PENDING)
        self.assertFalse(applicant.is_active)
        self.assertEqual(applicant.role, UserRole.DEPARTMENT_ADMIN)

        new_dept = Department.objects.get(code="GREEN")
        self.assertEqual(new_dept.approval_status, Department.ApprovalStatus.PENDING)
        self.assertFalse(new_dept.is_active)

    # -------------------------------------------------------------------------
    # 3. JWT Login Tests (Both Frontends)
    # -------------------------------------------------------------------------
    def test_login_success_react_client(self):
        url = "/auth/login/"
        data = {
            "email": "roadadmin@cirp.gov.et",
            "password": "RoadPassword123!"
        }
        # React client (standard browser User-Agent)
        response = self.client.post(url, data, format='json', HTTP_USER_AGENT="Mozilla/5.0")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        res_data = response.json()
        # Direct parsing matching React LoginResponseSchema: { access, refresh, user }
        self.assertIn("access", res_data)
        self.assertIn("refresh", res_data)
        self.assertIn("user", res_data)
        self.assertEqual(res_data["user"]["email"], "roadadmin@cirp.gov.et")
        self.assertEqual(res_data["user"]["role"], UserRole.DEPARTMENT_ADMIN)
        self.assertEqual(res_data["user"]["department"]["code"], "ROAD")

    def test_login_success_flutter_client(self):
        url = "/api/v1/auth/login/"
        data = {
            "email": "citizen@cirp.gov.et",
            "password": "CitizenPassword123!"
        }
        # Flutter client User-Agent
        response = self.client.post(url, data, format='json', HTTP_USER_AGENT="Dart/3.4 (dart:io)")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        res_data = response.json()
        # Envelope parsing matching Flutter: { success: true, message: ..., data: ... }
        self.assertTrue(res_data.get("success"))
        self.assertIn("data", res_data)
        self.assertIn("access", res_data["data"])
        self.assertIn("tokens", res_data["data"])
        self.assertIn("user", res_data["data"])
        self.assertEqual(res_data["data"]["user"]["email"], "citizen@cirp.gov.et")

    def test_login_invalid_password(self):
        url = "/auth/login/"
        data = {
            "email": "roadadmin@cirp.gov.et",
            "password": "WrongPassword123!"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_pending_user_cannot_login(self):
        # Create pending user
        User.objects.create_user(
            email="pending@cirp.gov.et",
            password="Password123!",
            role=UserRole.DEPARTMENT_ADMIN,
            status=User.StatusChoices.PENDING,
            is_active=False
        )
        url = "/auth/login/"
        data = {
            "email": "pending@cirp.gov.et",
            "password": "Password123!"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # -------------------------------------------------------------------------
    # 4. Protected Endpoints & Role-Based Permissions
    # -------------------------------------------------------------------------
    def test_profile_requires_authentication(self):
        url = "/api/v1/users/me/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_profile_access_with_jwt_bearer(self):
        # Authenticate with citizen token
        self.client.force_authenticate(user=self.citizen)
        url = "/api/v1/users/me/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        res_data = response.json()
        self.assertEqual(res_data["email"], "citizen@cirp.gov.et")

    def test_users_list_forbidden_for_citizen(self):
        self.client.force_authenticate(user=self.citizen)
        url = "/api/v1/users/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_users_list_allowed_for_system_admin(self):
        self.client.force_authenticate(user=self.system_admin)
        url = "/api/v1/users/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
