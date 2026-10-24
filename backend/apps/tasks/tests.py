from datetime import timedelta
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
from apps.extensions.models import Extension
from utils.enums import (
    UserRole,
    ReportStatus,
    TaskPriority,
    TaskStatus,
    TaskExtensionStatus,
    StaffRoleType,
)


class TaskManagementPipelineTestCase(APITestCase):
    def setUp(self):
        # 1. Departments
        self.road_dept = Department.objects.create(
            code="ROAD_M5",
            name="Road Authority M5",
            approval_status=Department.ApprovalStatus.APPROVED,
            is_active=True,
        )
        self.water_dept = Department.objects.create(
            code="WATER_M5",
            name="Water Authority M5",
            approval_status=Department.ApprovalStatus.APPROVED,
            is_active=True,
        )

        # 2. Categories
        self.road_cat = Category.objects.create(
            code="road_cat_m5",
            name="Road Maintenance M5",
            default_department=self.road_dept,
            is_active=True,
        )

        # 3. Staff / Contractors
        self.road_worker_1 = StaffContractor.objects.create(
            name="Kassahun Paving Lead",
            phone_number="+251911800101",
            email="kassahun_m5@cirp.gov.et",
            department=self.road_dept,
            role_type=StaffRoleType.STAFF_OFFICER,
            position_title="Senior Paving Engineer",
            is_available=True,
        )
        self.road_worker_2 = StaffContractor.objects.create(
            name="Addis Asphalt Corp Lead",
            phone_number="+251911800102",
            email="contractor_m5@addisasphalt.et",
            department=self.road_dept,
            role_type=StaffRoleType.CONTRACTOR_LEAD,
            position_title="Contractor Supervisor",
            is_contractor=True,
            contractor_company_name="Addis Asphalt Corp",
            license_number="LIC-ET-ROAD-2026",
            is_available=True,
        )
        self.water_worker = StaffContractor.objects.create(
            name="Tewodros Water Lead",
            phone_number="+251911800201",
            email="tewodros_m5@cirp.gov.et",
            department=self.water_dept,
            role_type=StaffRoleType.STAFF_OFFICER,
            position_title="Hydraulic Specialist",
            is_available=True,
        )

        # 4. Users
        self.citizen = User.objects.create_user(
            email="citizen_m5@cirp.com",
            password="testpassword123",
            first_name="Abebe",
            last_name="Bikila",
            role=UserRole.CITIZEN,
        )
        self.road_admin = User.objects.create_user(
            email="road_admin_m5@cirp.com",
            password="testpassword123",
            first_name="Berhanu",
            last_name="RoadAdmin",
            role=UserRole.DEPARTMENT_ADMIN,
            department=self.road_dept,
            is_staff=True,
        )
        self.water_admin = User.objects.create_user(
            email="water_admin_m5@cirp.com",
            password="testpassword123",
            first_name="Helen",
            last_name="WaterAdmin",
            role=UserRole.DEPARTMENT_ADMIN,
            department=self.water_dept,
            is_staff=True,
        )
        self.system_admin = User.objects.create_user(
            email="sys_admin_m5@cirp.com",
            password="testpassword123",
            first_name="Dawit",
            last_name="CityAdmin",
            role=UserRole.SYSTEM_ADMIN,
            is_staff=True,
            is_superuser=True,
        )

        # 5. Reports & Tasks
        self.road_report = Report.objects.create(
            report_code="REP-2026-M501",
            title="Road Sinkhole Incident",
            description="Asphalt depression on main avenue",
            category=self.road_cat,
            department=self.road_dept,
            latitude=9.005,
            longitude=38.763,
            status=ReportStatus.ACCEPTED,
        )
        self.now = timezone.now()
        self.initial_deadline = self.now + timedelta(days=7)

        self.road_task = Task.objects.create(
            task_code="TSK-2026-M501",
            report=self.road_report,
            department=self.road_dept,
            assigned_worker=self.road_worker_1,
            priority=TaskPriority.HIGH,
            status=TaskStatus.ASSIGNED,
            work_description="Excavate base and repave 50m asphalt section.",
            deadline_date=self.initial_deadline,
            original_deadline_date=self.initial_deadline,
            progress_percentage=0,
        )

        # JWT helpers
        self.citizen_token = str(RefreshToken.for_user(self.citizen).access_token)
        self.road_admin_token = str(RefreshToken.for_user(self.road_admin).access_token)
        self.water_admin_token = str(RefreshToken.for_user(self.water_admin).access_token)
        self.system_admin_token = str(RefreshToken.for_user(self.system_admin).access_token)

    # -------------------------------------------------------------------------
    # 1. Task Listing, Retrieval & Department Scoping Tests
    # -------------------------------------------------------------------------
    def test_task_list_department_isolation(self):
        """Road Admin only sees Road tasks; Water Admin only sees Water tasks; System Admin sees all."""
        # Create a water report and task
        water_rep = Report.objects.create(
            report_code="REP-2026-M502",
            title="Water Pipe Burst",
            description="Pipe leak on street",
            category=self.road_cat,
            department=self.water_dept,
            latitude=9.01,
            longitude=38.77,
            status=ReportStatus.ACCEPTED,
        )
        Task.objects.create(
            task_code="TSK-2026-M502",
            report=water_rep,
            department=self.water_dept,
            assigned_worker=self.water_worker,
            work_description="Weld replacement pipe section",
            deadline_date=self.initial_deadline,
            original_deadline_date=self.initial_deadline,
        )

        # Road Admin requests tasks
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.road_admin_token}")
        res = self.client.get("/api/v1/tasks/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        task_codes = [t["task_code"] for t in res.data]
        self.assertIn("TSK-2026-M501", task_codes)
        self.assertNotIn("TSK-2026-M502", task_codes)

        # System Admin sees both
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.system_admin_token}")
        res_sys = self.client.get("/api/v1/tasks/")
        self.assertEqual(res_sys.status_code, status.HTTP_200_OK)
        all_codes = [t["task_code"] for t in res_sys.data]
        self.assertIn("TSK-2026-M501", all_codes)
        self.assertIn("TSK-2026-M502", all_codes)

    def test_task_list_filters(self):
        """Filter tasks by status, search query, and overdue flag."""
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.road_admin_token}")

        # Status filter
        res = self.client.get("/api/v1/tasks/?status=ASSIGNED")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(len(res.data) >= 1)

        # Search filter
        res_search = self.client.get("/api/v1/tasks/?search=Sinkhole")
        self.assertEqual(res_search.status_code, status.HTTP_200_OK)
        self.assertEqual(res_search.data[0]["task_code"], "TSK-2026-M501")

    def test_task_detail_with_extensions(self):
        """Single task detail returns complete TaskRecordSchema with embedded extensions."""
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.road_admin_token}")
        res = self.client.get(f"/api/v1/tasks/{self.road_task.id}/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        data = res.data
        self.assertEqual(data["task_code"], "TSK-2026-M501")
        self.assertEqual(data["assigned_worker_name"], "Kassahun Paving Lead")
        self.assertIsInstance(data["extensions"], list)

    def test_citizen_forbidden_from_tasks(self):
        """Citizens cannot view or modify municipal operational tasks."""
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.citizen_token}")
        res = self.client.get("/api/v1/tasks/")
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

        res_detail = self.client.get(f"/api/v1/tasks/{self.road_task.id}/")
        self.assertEqual(res_detail.status_code, status.HTTP_403_FORBIDDEN)

    # -------------------------------------------------------------------------
    # 2. Worker Assignment & Reassignment Tests
    # -------------------------------------------------------------------------
    def test_reassign_worker_success(self):
        """Department Admin reassigns task to another authorized worker; logs progress note."""
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.road_admin_token}")
        url = f"/api/v1/tasks/{self.road_task.id}/"
        payload = {
            "assignedWorkerId": str(self.road_worker_2.id),
            "priority": "CRITICAL",
        }
        res = self.client.patch(url, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["assigned_worker_name"], "Addis Asphalt Corp Lead")
        self.assertEqual(res.data["priority"], "CRITICAL")

        # Verify audit progress note created
        self.road_task.refresh_from_db()
        self.assertEqual(self.road_task.assigned_worker, self.road_worker_2)
        audit_note = self.road_task.progress_notes[-1]
        self.assertIn("Task reassigned", audit_note["note"])

    def test_reassign_worker_cross_department_forbidden(self):
        """Cannot assign a worker belonging to a different department."""
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.road_admin_token}")
        url = f"/api/v1/tasks/{self.road_task.id}/"
        payload = {"assignedWorkerId": str(self.water_worker.id)}
        res = self.client.patch(url, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    # -------------------------------------------------------------------------
    # 3. Progress Tracking Tests
    # -------------------------------------------------------------------------
    def test_update_task_progress_appends_notes(self):
        """Updating progress updates percentage, logs author note, and updates Report status."""
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.road_admin_token}")
        url = f"/api/v1/tasks/{self.road_task.id}/progress/"
        payload = {
            "taskId": str(self.road_task.id),
            "progressPercentage": 45,
            "newStatus": "IN_PROGRESS",
            "progressNote": "Asphalt milled, base gravel laid and leveled.",
            "authorName": "Kassahun Paving Lead",
        }
        res = self.client.post(url, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["progress_percentage"], 45)
        self.assertEqual(res.data["status"], "IN_PROGRESS")

        # Verify parent report status synchronized to IN_PROGRESS
        self.road_report.refresh_from_db()
        self.assertEqual(self.road_report.status, ReportStatus.IN_PROGRESS)

    def test_cannot_update_progress_on_resolved_task(self):
        """Cannot update progress on a task that is already marked RESOLVED."""
        self.road_task.status = TaskStatus.RESOLVED
        self.road_task.save()

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.road_admin_token}")
        url = f"/api/v1/tasks/{self.road_task.id}/progress/"
        res = self.client.post(url, {
            "progressPercentage": 100,
            "newStatus": "RESOLVED",
            "progressNote": "Trying to update resolved task",
            "authorName": "Test",
        }, format="json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    # -------------------------------------------------------------------------
    # 4. Contractor Completion & Review Lifecycle Tests
    # -------------------------------------------------------------------------
    def test_submit_task_completion(self):
        """Contractor submits work completion; sets COMPLETED_PENDING_VERIFICATION."""
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.road_admin_token}")
        url = f"/api/v1/tasks/{self.road_task.id}/complete/"
        payload = {
            "taskId": str(self.road_task.id),
            "completionNotes": "All asphalt repaved and rolled. Lane opened.",
            "completionDate": self.now.isoformat(),
            "beforePhotos": ["/media/reports/before1.jpg"],
            "afterPhotos": ["/media/tasks/after1.jpg"],
            "submittedBy": "Addis Asphalt Corp Lead",
        }
        res = self.client.post(url, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["status"], "COMPLETED_PENDING_VERIFICATION")
        self.assertEqual(res.data["progress_percentage"], 100)

        # Parent report is also updated
        self.road_report.refresh_from_db()
        self.assertEqual(self.road_report.status, ReportStatus.COMPLETED_PENDING_VERIFICATION)

    def test_verify_resolve_task(self):
        """Department Admin inspects work and verifies resolution; returns boolean true."""
        self.road_task.status = TaskStatus.COMPLETED_PENDING_VERIFICATION
        self.road_task.save()

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.road_admin_token}")
        url = f"/api/v1/tasks/{self.road_task.id}/verify-resolve/"
        payload = {
            "taskId": str(self.road_task.id),
            "officerName": "Eng. Berhanu Wolde",
            "resolutionNotes": "Pavement density and grade inspected on site. Accepted.",
        }
        res = self.client.post(url, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, True)

        self.road_task.refresh_from_db()
        self.assertEqual(self.road_task.status, TaskStatus.RESOLVED)
        self.assertIsNotNone(self.road_task.resolved_at)

        self.road_report.refresh_from_db()
        self.assertEqual(self.road_report.status, ReportStatus.RESOLVED)
        self.assertIn("Eng. Berhanu Wolde", self.road_report.resolution_notes)

    def test_return_reject_task(self):
        """Admin returns substandard work for rework; records rejection history."""
        self.road_task.status = TaskStatus.COMPLETED_PENDING_VERIFICATION
        self.road_task.save()

        new_date = self.now + timedelta(days=5)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.road_admin_token}")
        url = f"/api/v1/tasks/{self.road_task.id}/return-reject/"
        payload = {
            "taskId": str(self.road_task.id),
            "officerName": "Eng. Berhanu Wolde",
            "reason": "Edge joint uneven; puddling occurs along gutter.",
            "requiredCorrection": "Re-mill joint and compact with hot mix.",
            "newExpectedDate": new_date.isoformat(),
        }
        res = self.client.post(url, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, True)

        self.road_task.refresh_from_db()
        self.assertEqual(self.road_task.status, TaskStatus.RETURNED)
        self.assertEqual(len(self.road_task.rejection_history), 1)
        self.assertIn("Edge joint uneven", self.road_task.rejection_history[0]["reason"])

        self.road_report.refresh_from_db()
        self.assertEqual(self.road_report.status, ReportStatus.IN_PROGRESS)

    # -------------------------------------------------------------------------
    # 5. Deadline Extensions Lifecycle Tests
    # -------------------------------------------------------------------------
    def test_request_extension_success(self):
        """Worker requests deadline extension with valid reason category and future date."""
        new_deadline = self.initial_deadline + timedelta(days=4)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.road_admin_token}")
        url = "/api/v1/extensions/"
        payload = {
            "taskId": str(self.road_task.id),
            "requestedNewDeadline": new_deadline.isoformat(),
            "reasonCategory": "Specialized equipment delivery delay",
            "detailedExplanation": "Asphalt paver hydraulic failure, parts arriving Thursday.",
            "supportingEvidenceNote": "Equipment vendor invoice #4881",
            "requestedBy": "Kassahun Paving Lead",
        }
        res = self.client.post(url, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data["status"], "PENDING")
        self.assertEqual(res.data["task_code"], "TSK-2026-M501")

        ext = Extension.objects.get(id=res.data["id"])
        self.assertEqual(ext.status, TaskExtensionStatus.PENDING)

    def test_request_extension_invalid_deadline(self):
        """Requested deadline must be after the current deadline."""
        past_deadline = self.initial_deadline - timedelta(days=1)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.road_admin_token}")
        url = "/api/v1/extensions/"
        res = self.client.post(url, {
            "taskId": str(self.road_task.id),
            "requestedNewDeadline": past_deadline.isoformat(),
            "reasonCategory": "Waiting for spare parts",
            "detailedExplanation": "Test invalid",
        }, format="json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_decide_extension_approve(self):
        """Admin approves deadline extension; task deadline is extended."""
        new_deadline = self.initial_deadline + timedelta(days=6)
        ext = Extension.objects.create(
            task=self.road_task,
            requested_by=self.road_admin,
            requested_by_name="Kassahun Paving Lead",
            original_deadline=self.road_task.deadline_date,
            requested_new_deadline=new_deadline,
            reason_category="Waiting for spare parts",
            detailed_explanation="Waiting for asphalt binder supply",
            status=TaskExtensionStatus.PENDING,
        )

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.road_admin_token}")
        url = f"/api/v1/extensions/{ext.id}/decide/"
        payload = {
            "extensionId": str(ext.id),
            "approve": True,
            "decidedBy": "Eng. Berhanu Wolde",
            "decisionComment": "Approved. Complete paving immediately upon material arrival.",
        }
        res = self.client.post(url, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, True)

        ext.refresh_from_db()
        self.assertEqual(ext.status, TaskExtensionStatus.APPROVED)

        self.road_task.refresh_from_db()
        self.assertEqual(self.road_task.deadline_date, new_deadline)

    def test_decide_extension_reject(self):
        """Admin rejects deadline extension; task deadline remains unchanged."""
        new_deadline = self.initial_deadline + timedelta(days=6)
        ext = Extension.objects.create(
            task=self.road_task,
            requested_by=self.road_admin,
            original_deadline=self.road_task.deadline_date,
            requested_new_deadline=new_deadline,
            reason_category="Additional technician crew needed",
            detailed_explanation="Want more time",
            status=TaskExtensionStatus.PENDING,
        )

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.road_admin_token}")
        url = f"/api/v1/extensions/{ext.id}/decide/"
        payload = {
            "extensionId": str(ext.id),
            "approve": False,
            "decidedBy": "Eng. Berhanu Wolde",
            "decisionComment": "Rejected. Priority project cannot slip.",
        }
        res = self.client.post(url, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, True)

        ext.refresh_from_db()
        self.assertEqual(ext.status, TaskExtensionStatus.REJECTED)

        self.road_task.refresh_from_db()
        self.assertEqual(self.road_task.deadline_date, self.initial_deadline)

    # -------------------------------------------------------------------------
    # 6. Contractor Management Tests
    # -------------------------------------------------------------------------
    def test_contractor_list_and_provision(self):
        """Department Admin creates an external contractor; validates license and company."""
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.road_admin_token}")
        url = "/api/v1/contractors/"

        # Missing company for external contractor -> 400
        res_fail = self.client.post(url, {
            "name": "Rapid Paving Ltd",
            "phone_number": "+251911333444",
            "email": "info@rapidpaving.et",
            "department_id": str(self.road_dept.id),
            "role_type": "CONTRACTOR_LEAD",
            "position_title": "Lead Contractor",
            "specialization": "Emergency Patching",
            "is_contractor": True,
        }, format="json")
        self.assertEqual(res_fail.status_code, status.HTTP_400_BAD_REQUEST)

        # Valid contractor creation
        res_ok = self.client.post(url, {
            "name": "Rapid Paving Ltd",
            "phone_number": "+251911333444",
            "email": "info@rapidpaving.et",
            "department_id": str(self.road_dept.id),
            "role_type": "CONTRACTOR_LEAD",
            "position_title": "Lead Contractor",
            "specialization": "Emergency Patching",
            "is_contractor": True,
            "contractor_company_name": "Rapid Paving Corporation",
            "license_number": "LIC-ET-PAVE-9912",
        }, format="json")
        self.assertEqual(res_ok.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res_ok.data["name"], "Rapid Paving Ltd")
        self.assertEqual(res_ok.data["contractor_company"], "Rapid Paving Corporation")

    def test_contractor_assigned_tasks(self):
        """Retrieve tasks assigned to a specific contractor worker."""
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.road_admin_token}")
        url = f"/api/v1/contractors/{self.road_worker_1.id}/tasks/"
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]["task_code"], "TSK-2026-M501")

    def test_cross_department_admin_cannot_modify_task(self):
        """Water Department Admin cannot update progress or verify Road Department tasks."""
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.water_admin_token}")
        url = f"/api/v1/tasks/{self.road_task.id}/progress/"
        res = self.client.post(url, {
            "progressPercentage": 50,
            "newStatus": "IN_PROGRESS",
            "progressNote": "Cross department attempt",
            "authorName": "Helen",
        }, format="json")
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
