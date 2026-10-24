import base64
from unittest.mock import patch
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from apps.users.models import User
from apps.departments.models import Department
from apps.categories.models import Category
from apps.assets.models import Asset, AssetType
from apps.contractors.models import StaffContractor
from apps.reports.models import Report
from apps.tasks.models import Task
from utils.enums import UserRole, ReportStatus, TaskPriority, TaskStatus, StaffRoleType


# 1x1 transparent PNG in base64
TINY_PNG_B64 = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="


class ReportsPipelineTestCase(APITestCase):
    def setUp(self):
        # 1. Departments
        self.road_dept = Department.objects.create(
            code="ROAD_T",
            name="Road & Transport Authority",
            approval_status=Department.ApprovalStatus.APPROVED,
            is_active=True,
        )
        self.water_dept = Department.objects.create(
            code="WATER_T",
            name="Water Supply & Sewerage",
            approval_status=Department.ApprovalStatus.APPROVED,
            is_active=True,
        )

        # 2. Categories
        self.cat_pothole = Category.objects.create(
            code="road_damage_t",
            name="Road Damage & Potholes",
            default_department=self.road_dept,
            is_active=True,
        )
        self.cat_water = Category.objects.create(
            code="water_leakage_t",
            name="Water Leakage & Pipe Burst",
            default_department=self.water_dept,
            is_active=True,
        )

        # 3. Users
        self.citizen = User.objects.create_user(
            email="citizen_test@cirp.com",
            password="testpassword123",
            first_name="Abebe",
            last_name="Citizen",
            role=UserRole.CITIZEN,
            phone_number="+251911999001",
        )
        self.road_admin = User.objects.create_user(
            email="road_admin_test@cirp.com",
            password="testpassword123",
            first_name="Berhanu",
            last_name="RoadAdmin",
            role=UserRole.DEPARTMENT_ADMIN,
            department=self.road_dept,
            is_staff=True,
        )
        self.water_admin = User.objects.create_user(
            email="water_admin_test@cirp.com",
            password="testpassword123",
            first_name="Helen",
            last_name="WaterAdmin",
            role=UserRole.DEPARTMENT_ADMIN,
            department=self.water_dept,
            is_staff=True,
        )
        self.system_admin = User.objects.create_user(
            email="system_admin_test@cirp.com",
            password="testpassword123",
            first_name="Dawit",
            last_name="SysAdmin",
            role=UserRole.SYSTEM_ADMIN,
            is_staff=True,
            is_superuser=True,
        )

        # 4. Staff / Contractors
        self.road_worker = StaffContractor.objects.create(
            name="Kassahun Road Tech",
            phone_number="+251911800101",
            email="kassahun_t@cirp.gov.et",
            department=self.road_dept,
            role_type=StaffRoleType.FIELD_TECHNICIAN,
            position_title="Senior Paving Tech",
            is_available=True,
        )

        # 5. Asset Type & Asset
        self.asset_type = AssetType.objects.create(
            id="asphalt_road_t",
            name="Asphalt Roadway",
            responsible_department=self.road_dept,
        )
        self.road_asset = Asset.objects.create(

            asset_code="AST-ROAD-001",
            name="Bole Road Arterial Section A",
            department=self.road_dept,
            asset_type=self.asset_type,
            latitude=9.0054,
            longitude=38.7636,
        )

        # JWT helpers
        self.citizen_token = str(RefreshToken.for_user(self.citizen).access_token)
        self.road_admin_token = str(RefreshToken.for_user(self.road_admin).access_token)
        self.water_admin_token = str(RefreshToken.for_user(self.water_admin).access_token)
        self.system_admin_token = str(RefreshToken.for_user(self.system_admin).access_token)

    # -------------------------------------------------------------------------
    # 1. Citizen Report Submission Tests
    # -------------------------------------------------------------------------
    def test_citizen_report_submission_success(self):
        """Citizen submits valid incident report with base64 photo and GPS."""
        url = "/api/v1/reports/"
        payload = {
            "title": "Severe Pothole on Bole Road",
            "description": "Deep pothole damaging car tires near the roundabout.",
            "category_id": str(self.cat_pothole.id),
            "latitude": 9.0054,
            "longitude": 38.7636,
            "priority": "HIGH",
            "address": "Bole Road, Addis Ababa",
            "media_images": [TINY_PNG_B64],
        }
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.citizen_token}")
        response = self.client.post(url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        data = response.data
        self.assertTrue(data["report_code"].startswith("REP-"))
        self.assertEqual(data["title"], "Severe Pothole on Bole Road")
        self.assertEqual(data["status"], "NEW")
        self.assertEqual(data["citizen_name"], "Abebe Citizen")
        self.assertEqual(len(data["media_photos"]), 1)

        # Verify DB entry
        report = Report.objects.get(report_code=data["report_code"])
        self.assertEqual(report.citizen, self.citizen)
        self.assertEqual(report.department, self.road_dept)
        self.assertEqual(report.status, ReportStatus.NEW)

    def test_report_submission_invalid_coordinates(self):
        """Latitude and longitude bounds validation (-90..90, -180..180)."""
        url = "/api/v1/reports/"
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.citizen_token}")

        # Out-of-bounds latitude
        res_lat = self.client.post(url, {
            "title": "Invalid Lat",
            "description": "Test",
            "category_id": self.cat_pothole.code,
            "latitude": 95.0,  # Invalid
            "longitude": 38.76,
        }, format="json")
        self.assertEqual(res_lat.status_code, status.HTTP_400_BAD_REQUEST)

        # Out-of-bounds longitude
        res_lon = self.client.post(url, {
            "title": "Invalid Lon",
            "description": "Test",
            "category_id": self.cat_pothole.code,
            "latitude": 9.0,
            "longitude": -195.0,  # Invalid
        }, format="json")
        self.assertEqual(res_lon.status_code, status.HTTP_400_BAD_REQUEST)

    def test_report_submission_client_cannot_tamper_administrative_fields(self):
        """Client supplying status='ACCEPTED' or fake citizen ID is overridden."""
        url = "/api/v1/reports/"
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.citizen_token}")
        payload = {
            "title": "Tamper Attempt",
            "description": "Citizen trying to mark report as accepted",
            "category_id": self.cat_pothole.code,
            "latitude": 9.0054,
            "longitude": 38.7636,
            "status": "ACCEPTED",  # Client tries to self-accept
            "citizen_id": "00000000-0000-0000-0000-000000000000",
        }
        res = self.client.post(url, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data["status"], "NEW")
        self.assertEqual(res.data["citizen_name"], "Abebe Citizen")

    # -------------------------------------------------------------------------
    # 2. AI Microservice Gateway Tests
    # -------------------------------------------------------------------------
    @patch("utils.ai_client.classify_image")
    def test_ai_classification_success_integration(self, mock_classify):
        """When AI service responds, suggestion and confidence are stored in report."""
        mock_classify.return_value = {
            "suggested_category": "road_damage",
            "confidence": 0.94,
            "all_scores": {"road_damage": 0.94, "drainage": 0.04},
        }
        url = "/api/v1/reports/"
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.citizen_token}")
        res = self.client.post(url, {
            "description": "AI Classification Test",
            "category_id": self.cat_pothole.code,
            "latitude": 9.0054,
            "longitude": 38.7636,
            "media_images": [TINY_PNG_B64],
        }, format="json")

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        report = Report.objects.get(id=res.data["id"])
        self.assertEqual(report.ai_category_prediction.get("suggested_category"), "road_damage")
        self.assertEqual(report.ai_category_prediction.get("confidence"), 0.94)

    @patch("utils.ai_client.classify_image")
    def test_ai_service_offline_or_timeout_does_not_block_submission(self, mock_classify):
        """If AI service is offline or times out, report creation still succeeds."""
        mock_classify.side_effect = Exception("Connection timeout to Port 8001")

        url = "/api/v1/reports/"
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.citizen_token}")
        res = self.client.post(url, {
            "description": "Resilience test against offline AI service",
            "category_id": self.cat_pothole.code,
            "latitude": 9.0054,
            "longitude": 38.7636,
            "media_images": [TINY_PNG_B64],
        }, format="json")

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        report = Report.objects.get(id=res.data["id"])
        self.assertEqual(report.ai_category_prediction, {})

    # -------------------------------------------------------------------------
    # 3. Admin Report Triage & Permissions Tests
    # -------------------------------------------------------------------------
    def test_report_list_department_scoping(self):
        """Department Admin only sees reports belonging to their department."""
        # Create 1 road report and 1 water report
        road_rep = Report.objects.create(
            report_code="REP-2026-0001",
            title="Road Issue",
            description="Road Desc",
            category=self.cat_pothole,
            department=self.road_dept,
            latitude=9.0,
            longitude=38.7,
        )
        water_rep = Report.objects.create(
            report_code="REP-2026-0002",
            title="Water Issue",
            description="Water Desc",
            category=self.cat_water,
            department=self.water_dept,
            latitude=9.1,
            longitude=38.8,
        )

        # Road Admin requests reports
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.road_admin_token}")
        res = self.client.get("/api/v1/reports/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        report_codes = [r["report_code"] for r in res.data]
        self.assertIn("REP-2026-0001", report_codes)
        self.assertNotIn("REP-2026-0002", report_codes)

        # System Admin sees both
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.system_admin_token}")
        res_sys = self.client.get("/api/v1/reports/")
        self.assertEqual(res_sys.status_code, status.HTTP_200_OK)
        all_codes = [r["report_code"] for r in res_sys.data]
        self.assertIn("REP-2026-0001", all_codes)
        self.assertIn("REP-2026-0002", all_codes)

    def test_accept_report_creates_atomic_task(self):
        """Accepting a report atomically updates report status and creates exactly 1 Task."""
        report = Report.objects.create(
            report_code="REP-2026-5555",
            title="Pothole to Accept",
            description="Urgent fix required",
            category=self.cat_pothole,
            department=self.road_dept,
            latitude=9.005,
            longitude=38.763,
            status=ReportStatus.NEW,
        )

        url = f"/api/v1/reports/{report.id}/accept/"
        accept_payload = {
            "reportId": str(report.id),
            "priority": "HIGH",
            "assignedWorkerId": str(self.road_worker.id),
            "deadlineDate": timezone.now().isoformat(),
            "workDescription": "Deploy asphalt patch team with steam roller.",
            "internalNote": "High traffic zone, complete before rush hour.",
        }

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.road_admin_token}")
        res = self.client.post(url, accept_payload, format="json")

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(res.data["task_code"].startswith("TSK-"))
        self.assertEqual(res.data["assigned_worker_name"], "Kassahun Road Tech")

        # Verify DB report updated to ACCEPTED
        report.refresh_from_db()
        self.assertEqual(report.status, ReportStatus.ACCEPTED)

        # Verify Task created
        task_count = Task.objects.filter(report=report).count()
        self.assertEqual(task_count, 1)

        # Retrying accept must be idempotent and not create duplicate task
        res_retry = self.client.post(url, accept_payload, format="json")
        self.assertEqual(res_retry.status_code, status.HTTP_200_OK)
        self.assertEqual(Task.objects.filter(report=report).count(), 1)

    def test_citizen_cannot_accept_report(self):
        """Ordinary citizen cannot perform administrative triage actions."""
        report = Report.objects.create(
            report_code="REP-2026-6666",
            title="Citizen Accept Test",
            description="Testing authorization",
            category=self.cat_pothole,
            department=self.road_dept,
            latitude=9.005,
            longitude=38.763,
        )
        url = f"/api/v1/reports/{report.id}/accept/"
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.citizen_token}")
        res = self.client.post(url, {
            "assignedWorkerId": str(self.road_worker.id),
            "deadlineDate": timezone.now().isoformat(),
            "workDescription": "Hack attempt",
        }, format="json")
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_cross_department_admin_cannot_accept_report(self):
        """Water admin cannot accept reports belonging to Road department."""
        report = Report.objects.create(
            report_code="REP-2026-7777",
            title="Road Report for Water Admin",
            description="Desc",
            category=self.cat_pothole,
            department=self.road_dept,
            latitude=9.005,
            longitude=38.763,
        )
        url = f"/api/v1/reports/{report.id}/accept/"
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.water_admin_token}")
        res = self.client.post(url, {
            "assignedWorkerId": str(self.road_worker.id),
            "deadlineDate": timezone.now().isoformat(),
            "workDescription": "Cross-dept test",
        }, format="json")
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_reject_report_requires_reason(self):
        """Rejecting a report requires a documented reason with min 5 chars."""
        report = Report.objects.create(
            report_code="REP-2026-8888",
            title="Report to Reject",
            description="Desc",
            category=self.cat_pothole,
            department=self.road_dept,
            latitude=9.005,
            longitude=38.763,
            status=ReportStatus.NEW,
        )
        url = f"/api/v1/reports/{report.id}/reject/"
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.road_admin_token}")

        # Empty reason -> 400
        res_fail = self.client.post(url, {"reason": ""}, format="json")
        self.assertEqual(res_fail.status_code, status.HTTP_400_BAD_REQUEST)

        # Valid reason -> success
        res_ok = self.client.post(url, {
            "reason": "Duplicate submission already handled under TSK-2026-0012."
        }, format="json")
        self.assertEqual(res_ok.status_code, status.HTTP_200_OK)

        report.refresh_from_db()
        # In React Admin schema, rejected status is DISPUTED
        self.assertEqual(report.status, ReportStatus.DISPUTED)
        self.assertIn("Duplicate submission", report.rejection_reason)

    def test_link_asset_to_report(self):
        """Department admin links existing physical asset to report."""
        report = Report.objects.create(
            report_code="REP-2026-9999",
            title="Report to Link Asset",
            description="Desc",
            category=self.cat_pothole,
            department=self.road_dept,
            latitude=9.005,
            longitude=38.763,
        )
        url = f"/api/v1/reports/{report.id}/link-asset/"
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.road_admin_token}")

        # Valid link
        res_ok = self.client.post(url, {"assetId": str(self.road_asset.id)}, format="json")
        self.assertEqual(res_ok.status_code, status.HTTP_200_OK)
        self.assertEqual(res_ok.data, True)  # z.boolean() contract

        report.refresh_from_db()
        self.assertEqual(report.asset, self.road_asset)

        # Invalid asset ID
        res_invalid = self.client.post(url, {"assetId": "00000000-0000-0000-0000-000000000000"}, format="json")
        self.assertEqual(res_invalid.status_code, status.HTTP_400_BAD_REQUEST)

    # -------------------------------------------------------------------------
    # 4. Public Transparency Portal Tests
    # -------------------------------------------------------------------------
    def test_public_reports_endpoint_privacy_and_anonymous_access(self):
        """
        Public transparency portal allows anonymous access and enforces
        strict privacy whitelist (no citizen phone, name, exact GPS, or internal notes).
        """
        # Create report with sensitive citizen contact and internal details
        Report.objects.create(
            report_code="REP-PUB-001",
            title="Leaking Pipe at Residence",
            description="Main pipe burst spraying water onto street.",
            category=self.cat_water,
            department=self.water_dept,
            citizen=self.citizen,
            citizen_name="Private Citizen Name",
            citizen_contact="+251911999999",
            latitude=9.012345,
            longitude=38.765432,
            address="House 402, Woreda 03, Kirkos, Addis Ababa",
            status=ReportStatus.ACCEPTED,
        )

        # Anonymous request (NO Authorization header)
        self.client.credentials()  # clear credentials
        res = self.client.get("/api/v1/public/reports/")

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIsInstance(res.data, list)
        self.assertTrue(len(res.data) >= 1)

        pub_rep = next(r for r in res.data if r["reference"] == "REP-PUB-001")

        # Conforms to PublicReportSchema.strict():
        # Allowed keys ONLY: {"reference", "category", "status", "submitted_at", "general_location"}
        allowed_keys = {"reference", "category", "status", "submitted_at", "general_location"}
        self.assertEqual(set(pub_rep.keys()), allowed_keys)

        # Verify safe mapped status
        self.assertEqual(pub_rep["status"], "Work in progress")
        self.assertEqual(pub_rep["category"], "Water Leakage & Pipe Burst")

        # Verify generalized safe location (never raw private address with house numbers)
        self.assertNotIn("House 402", pub_rep["general_location"])
        self.assertIn("Kirkos, Addis Ababa", pub_rep["general_location"])

        # Verify sensitive fields are strictly excluded
        self.assertNotIn("citizen_name", pub_rep)
        self.assertNotIn("citizen_contact", pub_rep)
        self.assertNotIn("latitude", pub_rep)
        self.assertNotIn("longitude", pub_rep)
