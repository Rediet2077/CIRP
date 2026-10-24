from django.test import TestCase
from utils.enums import UserRole
from apps.users.models import User
from apps.departments.models import Department
from apps.categories.models import Category
from apps.reports.models import Report


class FoundationSmokeTest(TestCase):
    def test_create_user_and_department(self):
        dept = Department.objects.create(
            name="Roads & Transport Department",
            code="ROAD",
            contact_email="roads@cirp.gov.et"
        )
        self.assertEqual(dept.code, "ROAD")

        user = User.objects.create_user(
            email="roadadmin@cirp.gov.et",
            password="StrongPassword123!",
            first_name="Eng. Berhanu",
            last_name="Wolde",
            role=UserRole.DEPARTMENT_ADMIN,
            department=dept
        )
        self.assertEqual(user.role, UserRole.DEPARTMENT_ADMIN)
        self.assertEqual(user.department.name, "Roads & Transport Department")

        cat = Category.objects.create(
            name="Road Damage",
            code="road_damage",
            default_department=dept
        )

        rep = Report.objects.create(
            report_code="REP-2026-0001",
            title="Large Pothole near Bole Medhanialem",
            description="Deep pothole in middle lane",
            category=cat,
            department=dept,
            citizen=user,
            latitude=9.0192,
            longitude=38.7525,
            address="Bole Road, Addis Ababa"
        )
        self.assertEqual(rep.report_code, "REP-2026-0001")
        self.assertEqual(rep.latitude, 9.0192)
        self.assertEqual(rep.longitude, 38.7525)
