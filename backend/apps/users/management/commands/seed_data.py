import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from utils.enums import UserRole
from apps.departments.models import Department
from apps.categories.models import Category
from apps.assets.models import AssetType

User = get_user_model()


class Command(BaseCommand):
    help = "Idempotently seed municipal departments, initial categories, asset types, and verified demo accounts."

    def handle(self, *args, **options):
        self.stdout.write("Starting idempotent database seeding for CIRP platform...")

        # 1. Seed Asset Types (Matches React AssetTypeDefinitionSchema)
        asset_types_data = [
            ("street_light", "Street Lighting"),
            ("road", "Road & Pavement"),
            ("water_point", "Water Point & Pipe"),
            ("drainage", "Drainage & Sewer"),
            ("waste_bin", "Waste Bin & Dumpster"),
            ("public_building", "Public Building & Facility"),
        ]
        for at_id, at_name in asset_types_data:
            AssetType.objects.get_or_create(
                id=at_id,
                defaults={"name": at_name, "requires_location": True, "is_active": True}
            )

        # 2. Seed Municipal Departments (Matches React DEMO_PRESETS & ADMIN_CREDENTIALS.md)
        departments_data = [
            {
                "code": "CENT",
                "name": "Central Municipal Operations",
                "email": "operations@cirp.gov.et",
                "phone": "+251111000000",
                "location": "City Hall, Addis Ababa",
                "asset_types": ["public_building"],
            },
            {
                "code": "ROAD",
                "name": "Roads & Transport Department",
                "email": "roads@cirp.gov.et",
                "phone": "+251111111111",
                "location": "Megenagna Operations Hub, Addis Ababa",
                "asset_types": ["road"],
            },
            {
                "code": "WATER",
                "name": "Water & Sanitation Department",
                "email": "water@cirp.gov.et",
                "phone": "+251111222222",
                "location": "Bole Sub-city Yard, Addis Ababa",
                "asset_types": ["water_point"],
            },
            {
                "code": "ELEC",
                "name": "Electricity Department",
                "email": "electricity@cirp.gov.et",
                "phone": "+251111333333",
                "location": "Piazza Power Station, Addis Ababa",
                "asset_types": ["street_light"],
            },
            {
                "code": "DRAIN",
                "name": "Drainage & Flood Management",
                "email": "drainage@cirp.gov.et",
                "phone": "+251111444444",
                "location": "Kality Depot, Addis Ababa",
                "asset_types": ["drainage"],
            },
            {
                "code": "WASTE",
                "name": "Sanitation & Waste Management",
                "email": "waste@cirp.gov.et",
                "phone": "+251111555555",
                "location": "Repi Operations Facility, Addis Ababa",
                "asset_types": ["waste_bin"],
            },
            {
                "code": "LITE",
                "name": "Street Lighting Department",
                "email": "lighting@cirp.gov.et",
                "phone": "+251111666666",
                "location": "Gotera Technical Center, Addis Ababa",
                "asset_types": ["street_light"],
            },
            {
                "code": "BUILD",
                "name": "Public Facilities & Buildings",
                "email": "facilities@cirp.gov.et",
                "phone": "+251111777777",
                "location": "Arat Kilo Municipal Annex, Addis Ababa",
                "asset_types": ["public_building"],
            },
        ]

        department_map = {}
        for d in departments_data:
            dept, _ = Department.objects.update_or_create(
                code=d["code"],
                defaults={
                    "name": d["name"],
                    "contact_email": d["email"],
                    "contact_phone": d["phone"],
                    "office_location": d["location"],
                    "responsible_asset_types": d["asset_types"],
                    "approval_status": Department.ApprovalStatus.APPROVED,
                    "is_active": True,
                }
            )
            department_map[d["code"]] = dept

        # 3. Seed Core Problem Categories (Matches Flutter & AI microservice)
        categories_data = [
            ("road_damage", "Road Damage & Potholes", "ROAD"),
            ("garbage", "Waste Accumulation & Litter", "WASTE"),
            ("water_leakage", "Water Leakage & Pipe Burst", "WATER"),
            ("drainage", "Blocked Drains & Flooding", "DRAIN"),
            ("streetlight_failure", "Streetlight Malfunction", "LITE"),
            ("public_facility", "Public Building Damage", "BUILD"),
            ("electricity", "Electrical Grid Hazard", "ELEC"),
            ("other", "Other Public Infrastructure Inquiry", "CENT"),
        ]

        for code, name, dept_code in categories_data:
            Category.objects.update_or_create(
                code=code,
                defaults={
                    "name": name,
                    "default_department": department_map.get(dept_code),
                    "is_active": True,
                }
            )

        # 4. Seed Verified Demo Accounts
        # Default password is read from DEMO_PASSWORD env var or defaults to 'password123'
        demo_password = os.getenv("DEMO_PASSWORD", "password123")

        users_data = [
            # Super Admin (City Admin)
            {
                "email": "dawit.tadesse@cirp.gov.et",
                "first_name": "Eng. Dawit",
                "last_name": "Tadesse",
                "role": UserRole.SYSTEM_ADMIN,
                "phone": "+251911000001",
                "dept": "CENT",
                "is_staff": True,
                "is_superuser": True,
            },
            {
                "email": "superadmin@cirp.com",
                "first_name": "Super",
                "last_name": "Admin",
                "role": UserRole.SYSTEM_ADMIN,
                "phone": "+251911000002",
                "dept": "CENT",
                "is_staff": True,
                "is_superuser": True,
            },
            # Department Admins
            {
                "email": "berhanu.wolde@cirp.gov.et",
                "first_name": "Eng. Berhanu",
                "last_name": "Wolde",
                "role": UserRole.DEPARTMENT_ADMIN,
                "phone": "+251911100001",
                "dept": "ROAD",
                "is_staff": True,
            },
            {
                "email": "roadadmin@cirp.com",
                "first_name": "Road",
                "last_name": "Admin",
                "role": UserRole.DEPARTMENT_ADMIN,
                "phone": "+251911100002",
                "dept": "ROAD",
                "is_staff": True,
            },
            {
                "email": "helen.m@cirp.gov.et",
                "first_name": "Helen",
                "last_name": "Mengistu",
                "role": UserRole.DEPARTMENT_ADMIN,
                "phone": "+251911200001",
                "dept": "WATER",
                "is_staff": True,
            },
            {
                "email": "wateradmin@cirp.com",
                "first_name": "Water",
                "last_name": "Admin",
                "role": UserRole.DEPARTMENT_ADMIN,
                "phone": "+251911200002",
                "dept": "WATER",
                "is_staff": True,
            },
            {
                "email": "almaz.bekele@cirp.gov.et",
                "first_name": "Almaz",
                "last_name": "Bekele",
                "role": UserRole.DEPARTMENT_ADMIN,
                "phone": "+251911300001",
                "dept": "ELEC",
                "is_staff": True,
            },
            {
                "email": "electricityadmin@cirp.com",
                "first_name": "Electricity",
                "last_name": "Admin",
                "role": UserRole.DEPARTMENT_ADMIN,
                "phone": "+251911300002",
                "dept": "ELEC",
                "is_staff": True,
            },
            {
                "email": "yonas.girma@cirp.gov.et",
                "first_name": "Yonas",
                "last_name": "Girma",
                "role": UserRole.DEPARTMENT_ADMIN,
                "phone": "+251911400001",
                "dept": "DRAIN",
                "is_staff": True,
            },
            {
                "email": "drainageadmin@cirp.com",
                "first_name": "Drainage",
                "last_name": "Admin",
                "role": UserRole.DEPARTMENT_ADMIN,
                "phone": "+251911400002",
                "dept": "DRAIN",
                "is_staff": True,
            },
            {
                "email": "mulu.kebede@cirp.gov.et",
                "first_name": "Mulu",
                "last_name": "Kebede",
                "role": UserRole.DEPARTMENT_ADMIN,
                "phone": "+251911500001",
                "dept": "WASTE",
                "is_staff": True,
            },
            {
                "email": "wasteadmin@cirp.com",
                "first_name": "Waste",
                "last_name": "Admin",
                "role": UserRole.DEPARTMENT_ADMIN,
                "phone": "+251911500002",
                "dept": "WASTE",
                "is_staff": True,
            },
            {
                "email": "aster.desta@cirp.gov.et",
                "first_name": "Aster",
                "last_name": "Desta",
                "role": UserRole.DEPARTMENT_ADMIN,
                "phone": "+251911600001",
                "dept": "LITE",
                "is_staff": True,
            },
            {
                "email": "streetlightadmin@cirp.com",
                "first_name": "Streetlight",
                "last_name": "Admin",
                "role": UserRole.DEPARTMENT_ADMIN,
                "phone": "+251911600002",
                "dept": "LITE",
                "is_staff": True,
            },
            {
                "email": "selam.tesfaye@cirp.gov.et",
                "first_name": "Selam",
                "last_name": "Tesfaye",
                "role": UserRole.DEPARTMENT_ADMIN,
                "phone": "+251911700001",
                "dept": "BUILD",
                "is_staff": True,
            },
            {
                "email": "facilitiesadmin@cirp.com",
                "first_name": "Facilities",
                "last_name": "Admin",
                "role": UserRole.DEPARTMENT_ADMIN,
                "phone": "+251911700002",
                "dept": "BUILD",
                "is_staff": True,
            },
            # Citizens for Flutter Mobile Testing
            {
                "email": "citizen@cirp.gov.et",
                "first_name": "Abebe",
                "last_name": "Bikila",
                "role": UserRole.CITIZEN,
                "phone": "+251911223344",
                "dept": None,
                "is_staff": False,
            },
            {
                "email": "citizen@example.com",
                "first_name": "Derartu",
                "last_name": "Tulu",
                "role": UserRole.CITIZEN,
                "phone": "+251911223355",
                "dept": None,
                "is_staff": False,
            },
        ]

        created_count = 0
        updated_count = 0

        for u in users_data:
            user, created = User.objects.get_or_create(
                email=u["email"],
                defaults={
                    "first_name": u["first_name"],
                    "last_name": u["last_name"],
                    "phone_number": u["phone"],
                    "role": u["role"],
                    "status": User.StatusChoices.ACTIVE,
                    "is_active": True,
                    "is_verified": True,
                    "is_staff": u.get("is_staff", False),
                    "is_superuser": u.get("is_superuser", False),
                    "department": department_map.get(u["dept"]),
                }
            )

            # Ensure password and department are set idempotently
            user.set_password(demo_password)
            user.role = u["role"]
            user.status = User.StatusChoices.ACTIVE
            user.is_active = True
            user.is_verified = True
            user.department = department_map.get(u["dept"])
            user.save()

            # Assign department admin if applicable
            dept = department_map.get(u["dept"])
            if dept and u["role"] == UserRole.DEPARTMENT_ADMIN and not dept.admin_user:
                dept.admin_user = user
                dept.save(update_fields=["admin_user"])

            if created:
                created_count += 1
            else:
                updated_count += 1

        # 5. Seed Staff and Contractors for each department
        from apps.contractors.models import StaffContractor
        from utils.enums import StaffRoleType

        staff_data = [
            # ROAD
            {"name": "Kassahun Desta", "phone": "+251911800101", "email": "kassahun.road@cirp.gov.et", "dept": "ROAD", "role_type": StaffRoleType.STAFF_OFFICER, "title": "Senior Highway Engineer", "spec": "Asphalt Paving", "is_contractor": False},
            {"name": "Addis Asphalt Engineering Corp", "phone": "+251911800102", "email": "dispatch@addisasphalt.et", "dept": "ROAD", "role_type": StaffRoleType.CONTRACTOR_LEAD, "title": "Road Contractor Lead", "spec": "Pothole Patching & Resurfacing", "is_contractor": True, "company": "Addis Asphalt Corp", "license": "LIC-ET-ROAD-2024"},
            # WATER
            {"name": "Tewodros Kassaye", "phone": "+251911800201", "email": "tewodros.water@cirp.gov.et", "dept": "WATER", "role_type": StaffRoleType.STAFF_OFFICER, "title": "Lead Hydraulic Engineer", "spec": "Mains Pipe Repair", "is_contractor": False},
            {"name": "Blue Nile Plumbing & Utilities", "phone": "+251911800202", "email": "ops@bluenilewater.et", "dept": "WATER", "role_type": StaffRoleType.CONTRACTOR_LEAD, "title": "Utility Contractor Lead", "spec": "Pipeline Excavation & Welding", "is_contractor": True, "company": "Blue Nile Utilities", "license": "LIC-ET-WTR-8812"},
            # ELEC
            {"name": "Fikru Hailu", "phone": "+251911800301", "email": "fikru.elec@cirp.gov.et", "dept": "ELEC", "role_type": StaffRoleType.STAFF_OFFICER, "title": "Grid Maintenance Supervisor", "spec": "High-Voltage Distribution", "is_contractor": False},
            # DRAIN
            {"name": "Solomon Belay", "phone": "+251911800401", "email": "solomon.drain@cirp.gov.et", "dept": "DRAIN", "role_type": StaffRoleType.STAFF_OFFICER, "title": "Stormwater Drainage Specialist", "spec": "Culverts & Floodways", "is_contractor": False},
            # WASTE
            {"name": "Genet Tefera", "phone": "+251911800501", "email": "genet.waste@cirp.gov.et", "dept": "WASTE", "role_type": StaffRoleType.STAFF_OFFICER, "title": "Waste Logistics Officer", "spec": "Bulk Disposal & Transfer", "is_contractor": False},
            # LITE
            {"name": "Ermias Zeleke", "phone": "+251911800601", "email": "ermias.lite@cirp.gov.et", "dept": "LITE", "role_type": StaffRoleType.STAFF_OFFICER, "title": "Illumination Field Tech", "spec": "LED Fixtures & Poles", "is_contractor": False},
            # BUILD
            {"name": "Beshir Mohammed", "phone": "+251911800701", "email": "beshir.build@cirp.gov.et", "dept": "BUILD", "role_type": StaffRoleType.STAFF_OFFICER, "title": "Structural Inspector", "spec": "Public Buildings", "is_contractor": False},
        ]

        seeded_staff = 0
        for s in staff_data:
            dept = department_map.get(s["dept"])
            if dept:
                StaffContractor.objects.update_or_create(
                    email=s["email"],
                    defaults={
                        "name": s["name"],
                        "phone_number": s["phone"],
                        "department": dept,
                        "role_type": s["role_type"],
                        "position_title": s["title"],
                        "specialization": s["spec"],
                        "is_contractor": s.get("is_contractor", False),
                        "contractor_company_name": s.get("company", ""),
                        "license_number": s.get("license", ""),
                        "is_available": True,
                        "performance_score": 95.0,
                    }
                )
                seeded_staff += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully seeded: {len(departments_data)} departments, "
                f"{len(categories_data)} categories, {created_count + updated_count} demo user accounts, "
                f"and {seeded_staff} staff/contractor profiles."
            )
        )
