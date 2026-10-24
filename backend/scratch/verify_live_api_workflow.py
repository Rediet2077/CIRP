import os
import sys
from datetime import timedelta

# Ensure backend root is on sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
import django
django.setup()

from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework import status

from apps.users.models import User
from apps.departments.models import Department
from apps.categories.models import Category
from apps.contractors.models import StaffContractor
from apps.reports.models import Report
from apps.tasks.models import Task
from utils.enums import UserRole, ReportStatus, TaskStatus


def run_live_api_verification():
    print("=" * 70)
    print("STARTING LIVE API WORKFLOW VERIFICATION ON CIRP_DB")
    print("=" * 70)

    client = APIClient()

    # 1. Citizen Authentication via JWT
    print("\n--- 1. Testing Citizen Login (POST /api/v1/auth/login/) ---")
    login_res = client.post('/api/v1/auth/login/', {
        "email": "citizen@example.com",
        "password": "password123",
    }, format='json')

    if login_res.status_code != status.HTTP_200_OK:
        print(f"FAILED: Citizen login returned status {login_res.status_code}: {login_res.data}")
        return False

    citizen_token = login_res.data.get("access") or login_res.data.get("tokens", {}).get("access")
    print(f"SUCCESS: Citizen logged in. Access token acquired: {citizen_token[:20]}...")

    # 2. Citizen Report Submission via API
    print("\n--- 2. Testing Citizen Report Submission (POST /api/v1/reports/) ---")
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {citizen_token}")

    report_payload = {
        "title": "Live API Verified Sinkhole on Bole Ring Road",
        "description": "Deep asphalt depression causing major hazard for vehicles near Atlas.",
        "category_id": "road_damage",
        "latitude": 9.0065,
        "longitude": 38.7645,
        "priority": "HIGH",
        "address": "Bole Ring Road corridor near Atlas, Addis Ababa",
    }
    report_res = client.post('/api/v1/reports/', report_payload, format='json')

    if report_res.status_code != status.HTTP_201_CREATED:
        print(f"FAILED: Report submission returned {report_res.status_code}: {report_res.data}")
        return False

    report_data = report_res.data
    report_id = report_data["id"]
    report_code = report_data["report_code"]
    print(f"SUCCESS: Report created via API with Code: {report_code}, ID: {report_id}")
    print(f"Initial Status: {report_data.get('status')}, Dept: {report_data.get('department_name')}")

    # 3. Verify Database Persistence in PostgreSQL (cirp_db)
    print("\n--- 3. Verifying Report Persistence in cirp_db ---")
    db_report = Report.objects.filter(id=report_id).first()
    if not db_report:
        print("FAILED: Report not found in cirp_db!")
        return False
    print(f"SUCCESS: Found in cirp_db: {db_report.report_code} | Status: {db_report.status} | Dept: {db_report.department.code}")
    assert db_report.status == ReportStatus.NEW, "Expected status NEW"

    # 4. Road Department Admin Authentication via JWT
    print("\n--- 4. Testing Road Admin Login (POST /api/v1/auth/login/) ---")
    client.credentials()  # Clear citizen credentials
    road_login_res = client.post('/api/v1/auth/login/', {
        "email": "berhanu.wolde@cirp.gov.et",
        "password": "password123",
    }, format='json')

    if road_login_res.status_code != status.HTTP_200_OK:
        # Fallback to roadadmin@cirp.com
        road_login_res = client.post('/api/v1/auth/login/', {
            "email": "roadadmin@cirp.com",
            "password": "password123",
        }, format='json')

    if road_login_res.status_code != status.HTTP_200_OK:
        print(f"FAILED: Road admin login failed: {road_login_res.data}")
        return False

    road_admin_token = road_login_res.data.get("access") or road_login_res.data.get("tokens", {}).get("access")
    print(f"SUCCESS: Road Admin logged in. Access token acquired: {road_admin_token[:20]}...")

    # Fetch assigned road worker
    road_worker = StaffContractor.objects.filter(department__code="ROAD").first()
    assert road_worker is not None, "Road worker must exist"

    # 5. Department Admin Triage Acceptance (POST /api/v1/reports/<id>/accept/)
    print("\n--- 5. Testing Report Acceptance & Task Creation ---")
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {road_admin_token}")

    accept_url = f"/api/v1/reports/{report_id}/accept/"
    accept_payload = {
        "reportId": str(report_id),
        "priority": "HIGH",
        "assignedWorkerId": str(road_worker.id),
        "deadlineDate": (timezone.now() + timedelta(days=7)).isoformat(),
        "workDescription": "Milling damaged area and applying 50mm asphalt wearing course.",
        "internalNote": "Coordinate with traffic safety unit; night shift execution.",
    }
    accept_res = client.post(accept_url, accept_payload, format='json')

    if accept_res.status_code != status.HTTP_201_CREATED:
        print(f"FAILED: Report acceptance returned {accept_res.status_code}: {accept_res.data}")
        return False

    task_data = accept_res.data
    task_code = task_data["task_code"]
    print(f"SUCCESS: Task created via API with Task Code: {task_code}")
    print(f"Assigned Worker: {task_data.get('assigned_worker_name')} | Status: {task_data.get('status')}")

    # 6. Verify Exact One Task in PostgreSQL (cirp_db)
    print("\n--- 6. Verifying Database State for Report and Task ---")
    db_report.refresh_from_db()
    print(f"Report status after acceptance: {db_report.status}")
    assert db_report.status == ReportStatus.ACCEPTED, "Expected report status ACCEPTED"

    tasks_count = Task.objects.filter(report=db_report).count()
    print(f"Tasks count for this report: {tasks_count}")
    assert tasks_count == 1, f"Expected exactly 1 task, found {tasks_count}"

    # 7. Test Idempotency (Repeat Acceptance Request)
    print("\n--- 7. Testing Idempotent Repeat Call (POST accept again) ---")
    repeat_res = client.post(accept_url, accept_payload, format='json')
    print(f"Repeat accept response status: {repeat_res.status_code}")
    assert repeat_res.status_code == status.HTTP_200_OK, f"Expected 200 OK on repeat, got {repeat_res.status_code}"

    tasks_count_after = Task.objects.filter(report=db_report).count()
    print(f"Tasks count after repeat call: {tasks_count_after}")
    assert tasks_count_after == 1, f"Task count must remain 1, found {tasks_count_after}"

    # 8. Test Permissions & Department Isolation
    print("\n--- 8. Testing Authorization & Department Isolation ---")
    # A. Citizen attempts to accept a report -> 403 Forbidden
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {citizen_token}")
    citizen_accept_res = client.post(accept_url, accept_payload, format='json')
    print(f"Citizen accept attempt status: {citizen_accept_res.status_code} (Expected 403)")
    assert citizen_accept_res.status_code == status.HTTP_403_FORBIDDEN

    # B. Water Admin attempts to accept Road report -> 403 Forbidden
    water_login_res = client.post('/api/v1/auth/login/', {
        "email": "helen.m@cirp.gov.et",
        "password": "password123",
    }, format='json')
    if water_login_res.status_code != status.HTTP_200_OK:
        water_login_res = client.post('/api/v1/auth/login/', {
            "email": "wateradmin@cirp.com",
            "password": "password123",
        }, format='json')

    water_token = water_login_res.data.get("access") or water_login_res.data.get("tokens", {}).get("access")
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {water_token}")

    water_accept_res = client.post(accept_url, accept_payload, format='json')
    print(f"Water Admin accept Road report attempt: {water_accept_res.status_code} (Expected 403)")
    assert water_accept_res.status_code == status.HTTP_403_FORBIDDEN

    # C. Department Isolation on Task List
    water_tasks_res = client.get('/api/v1/tasks/')
    water_task_codes = [t["task_code"] for t in water_tasks_res.data]
    print(f"Water Admin tasks returned: {len(water_task_codes)} tasks")
    assert task_code not in water_task_codes, f"Water Admin must NOT see Road task {task_code}"
    print(f"SUCCESS: Road task {task_code} is hidden from Water Department Admin.")

    # D. Road Admin sees the new task
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {road_admin_token}")
    road_tasks_res = client.get('/api/v1/tasks/')
    road_task_codes = [t["task_code"] for t in road_tasks_res.data]
    assert task_code in road_task_codes, f"Road Admin must see Road task {task_code}"
    print(f"SUCCESS: Road Admin sees Road task {task_code}.")

    print("\n" + "=" * 70)
    print("ALL LIVE API WORKFLOW AND PERMISSION CHECKS PASSED WITH 100% SUCCESS!")
    print("=" * 70)
    return True


if __name__ == '__main__':
    success = run_live_api_verification()
    sys.exit(0 if success else 1)
