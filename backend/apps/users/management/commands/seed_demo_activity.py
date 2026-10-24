import os
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth import get_user_model

from apps.departments.models import Department
from apps.categories.models import Category
from apps.assets.models import Asset, AssetType
from apps.contractors.models import StaffContractor
from apps.reports.models import Report
from apps.tasks.models import Task
from apps.extensions.models import Extension
from utils.enums import (
    AssetStatus,
    AssetCondition,
    ReportPriority,
    ReportStatus,
    TaskPriority,
    TaskStatus,
    TaskExtensionStatus,
)

User = get_user_model()


class Command(BaseCommand):
    help = "Idempotently seed realistic demo assets, reports, tasks, and deadline extensions for frontend testing."

    def handle(self, *args, **options):
        self.stdout.write("Starting idempotent demo activity seeding for CIRP platform...")

        # 1. Fetch prerequisite users
        citizen = User.objects.filter(email="citizen@example.com").first() or User.objects.filter(role="CITIZEN").first()
        road_admin = User.objects.filter(email="berhanu.wolde@cirp.gov.et").first() or User.objects.filter(email="roadadmin@cirp.com").first()
        water_admin = User.objects.filter(email="helen.m@cirp.gov.et").first() or User.objects.filter(email="wateradmin@cirp.com").first()
        sys_admin = User.objects.filter(email="dawit.tadesse@cirp.gov.et").first() or User.objects.filter(email="superadmin@cirp.com").first()

        if not citizen or not road_admin:
            self.stdout.write(
                self.style.WARNING("Prerequisite users not found. Please run 'python manage.py seed_data' first.")
            )
            return

        # 2. Fetch prerequisite departments
        road_dept = Department.objects.filter(code="ROAD").first()
        water_dept = Department.objects.filter(code="WATER").first()
        lite_dept = Department.objects.filter(code="LITE").first()
        drain_dept = Department.objects.filter(code="DRAIN").first()
        waste_dept = Department.objects.filter(code="WASTE").first()

        # 3. Fetch categories
        road_cat = Category.objects.filter(code="road_damage").first()
        water_cat = Category.objects.filter(code="water_leakage").first()
        lite_cat = Category.objects.filter(code="streetlight_failure").first()
        drain_cat = Category.objects.filter(code="drainage").first()
        waste_cat = Category.objects.filter(code="garbage").first()

        # 4. Fetch staff / contractors
        road_staff = StaffContractor.objects.filter(email="kassahun.road@cirp.gov.et").first()
        road_contractor = StaffContractor.objects.filter(email="dispatch@addisasphalt.et").first()
        water_contractor = StaffContractor.objects.filter(email="ops@bluenilewater.et").first()
        lite_staff = StaffContractor.objects.filter(email="ermias.lite@cirp.gov.et").first()

        # 5. Seed Physical Assets (Idempotent by asset_code)
        now = timezone.now()
        road_type = AssetType.objects.filter(id="road").first()
        water_type = AssetType.objects.filter(id="water_point").first()
        lite_type = AssetType.objects.filter(id="street_light").first()
        drain_type = AssetType.objects.filter(id="drainage").first()

        assets_seeded = 0
        asset_records = [
            {
                "code": "AST-ROAD-001",
                "name": "Bole Road Arterial Section A",
                "desc": "Dual carriageway asphalt roadway connecting Meskel Square to Atlas.",
                "type": road_type,
                "dept": road_dept,
                "lat": 9.0054,
                "lng": 38.7636,
                "addr": "Bole Road near Atlas Hotel, Addis Ababa",
                "landmark": "Near Atlas Hotel Intersection",
                "condition": AssetCondition.FAIR,
            },
            {
                "code": "AST-ROAD-002",
                "name": "Megenagna Ring Road Overpass Pavement",
                "desc": "Heavy freight corridor pavement on outer ring road.",
                "type": road_type,
                "dept": road_dept,
                "lat": 9.0210,
                "lng": 38.7990,
                "addr": "Megenagna Roundabout Overpass, Addis Ababa",
                "landmark": "Megenagna Transit Hub",
                "condition": AssetCondition.POOR,
            },
            {
                "code": "AST-WTR-001",
                "name": "Bole Sub-City Water Main Gate Valve #14",
                "desc": "High pressure distribution valve box serving Bole commercial zone.",
                "type": water_type,
                "dept": water_dept,
                "lat": 8.9980,
                "lng": 38.7840,
                "addr": "Cameroon Street, Bole Sub-City, Addis Ababa",
                "landmark": "Near Medhanialem Cathedral",
                "condition": AssetCondition.GOOD,
            },
            {
                "code": "AST-LITE-001",
                "name": "Gotera Interchange LED Mast Array #3",
                "desc": "12-fixture 400W LED high-mast lighting pole.",
                "type": lite_type,
                "dept": lite_dept,
                "lat": 8.9880,
                "lng": 38.7490,
                "addr": "Gotera Interchange South Approach, Addis Ababa",
                "landmark": "Gotera Flyover Junction",
                "condition": AssetCondition.FAIR,
            },
            {
                "code": "AST-DRN-001",
                "name": "Kality Industrial Zone Storm Culvert B",
                "desc": "Reinforced concrete box culvert draining runoff towards Akaki river.",
                "type": drain_type,
                "dept": drain_dept,
                "lat": 8.9150,
                "lng": 38.7600,
                "addr": "Kality Industrial Road 4, Addis Ababa",
                "landmark": "Kality Depot Gate 2",
                "condition": AssetCondition.POOR,
            },
        ]

        asset_map = {}
        for a in asset_records:
            if a["type"] and a["dept"]:
                asset, created = Asset.objects.update_or_create(
                    asset_code=a["code"],
                    defaults={
                        "name": a["name"],
                        "description": a["desc"],
                        "asset_type": a["type"],
                        "department": a["dept"],
                        "status": AssetStatus.ACTIVE,
                        "condition": a["condition"],
                        "latitude": a["lat"],
                        "longitude": a["lng"],
                        "address": a["addr"],
                        "landmark": a["landmark"],
                        "registered_by": sys_admin,
                    }
                )
                asset_map[a["code"]] = asset
                if created:
                    assets_seeded += 1

        # 6. Seed Reports & Tasks across distinct lifecycle states
        # Scenario 1: Road Pothole -> ACCEPTED & Task IN_PROGRESS with progress notes & PENDING extension
        rep1, _ = Report.objects.update_or_create(
            report_code="REP-2026-DEMO-001",
            defaults={
                "title": "Severe Pothole on Bole Road near Atlas",
                "description": "Deep asphalt crater on inner northbound lane causing traffic swerving and tire damage.",
                "citizen": citizen,
                "citizen_name": citizen.get_full_name() or "Abebe Bikila",
                "citizen_contact": citizen.phone_number or "+251911223344",
                "category": road_cat,
                "department": road_dept,
                "asset": asset_map.get("AST-ROAD-001"),
                "latitude": 9.0054,
                "longitude": 38.7636,
                "address": "Bole Road near Atlas Hotel",
                "landmark": "In front of Atlas Hotel",
                "priority": ReportPriority.HIGH,
                "status": ReportStatus.IN_PROGRESS,
                "media_photos": ["/media/reports/demo_pothole_1.jpg"],
                "ai_category_prediction": {"suggested_category": "road_damage", "confidence": 0.96},
            }
        )

        task1, _ = Task.objects.update_or_create(
            task_code="TSK-2026-DEMO-001",
            defaults={
                "report": rep1,
                "department": road_dept,
                "assigned_worker": road_contractor or road_staff,
                "priority": TaskPriority.HIGH,
                "status": TaskStatus.IN_PROGRESS,
                "work_description": "Milling of 25m damaged asphalt section, gravel compaction, and 70mm hot-mix asphalt paving.",
                "internal_note": "Coordinate traffic safety crew; schedule heavy compaction outside peak hours.",
                "progress_percentage": 50,
                "original_deadline_date": now + timedelta(days=5),
                "deadline_date": now + timedelta(days=5),
                "progress_notes": [
                    {
                        "timestamp": (now - timedelta(days=2)).isoformat(),
                        "author": "Addis Asphalt Engineering Corp",
                        "note": "Work order accepted. Safety barriers and traffic detour deployed.",
                        "percentage": 10,
                    },
                    {
                        "timestamp": (now - timedelta(days=1)).isoformat(),
                        "author": "Addis Asphalt Engineering Corp",
                        "note": "Excavation and sub-base gravel leveling completed.",
                        "percentage": 50,
                    },
                ],
            }
        )

        # Pending deadline extension on Task 1
        Extension.objects.update_or_create(
            task=task1,
            reason_category="Specialized equipment delivery delay",
            defaults={
                "requested_by": road_admin,
                "requested_by_name": "Addis Asphalt Corp Lead",
                "original_deadline": task1.deadline_date,
                "requested_new_deadline": task1.deadline_date + timedelta(days=4),
                "detailed_explanation": "Asphalt paver breakdown on site. Replacement hydraulic pump in transit.",
                "supporting_evidence_note": "Vendor repair ticket #ET-9921",
                "status": TaskExtensionStatus.PENDING,
            }
        )

        # Scenario 2: Road Surface Depression -> COMPLETED_PENDING_VERIFICATION (Awaiting Admin sign-off)
        rep2, _ = Report.objects.update_or_create(
            report_code="REP-2026-DEMO-002",
            defaults={
                "title": "Megenagna Overpass Asphalt Depression",
                "description": "Rutting and asphalt wavy surface on overpass curve.",
                "citizen": citizen,
                "citizen_name": citizen.get_full_name() or "Abebe Bikila",
                "citizen_contact": citizen.phone_number or "+251911223344",
                "category": road_cat,
                "department": road_dept,
                "asset": asset_map.get("AST-ROAD-002"),
                "latitude": 9.0210,
                "longitude": 38.7990,
                "address": "Megenagna Ring Road Overpass",
                "landmark": "Near Megenagna Light Rail Station",
                "priority": ReportPriority.MEDIUM,
                "status": ReportStatus.COMPLETED_PENDING_VERIFICATION,
                "media_photos": ["/media/reports/demo_road_cracking.jpg"],
                "ai_category_prediction": {"suggested_category": "road_damage", "confidence": 0.92},
            }
        )

        Task.objects.update_or_create(
            task_code="TSK-2026-DEMO-002",
            defaults={
                "report": rep2,
                "department": road_dept,
                "assigned_worker": road_staff,
                "priority": TaskPriority.MEDIUM,
                "status": TaskStatus.COMPLETED_PENDING_VERIFICATION,
                "work_description": "Cold milling 40mm surface and applying polymer-modified binder course.",
                "internal_note": "Completed overnight to avoid public disruption.",
                "progress_percentage": 100,
                "original_deadline_date": now + timedelta(days=2),
                "deadline_date": now + timedelta(days=2),
                "progress_notes": [
                    {
                        "timestamp": (now - timedelta(days=1)).isoformat(),
                        "author": "Kassahun Desta",
                        "note": "Milling complete, hot-mix paving finished and rolled.",
                        "percentage": 100,
                    }
                ],
                "completion_submission": {
                    "completion_date": now.isoformat(),
                    "completion_notes": "All paving completed according to municipal highway specs. Lane opened.",
                    "before_photos": ["/media/reports/demo_road_cracking.jpg"],
                    "after_photos": ["/media/tasks/demo_road_completed.jpg"],
                    "submitted_by": "Kassahun Desta",
                },
            }
        )

        # Scenario 3: Water Pipe Burst -> RESOLVED (Complete historical record)
        rep3, _ = Report.objects.update_or_create(
            report_code="REP-2026-DEMO-003",
            defaults={
                "title": "High-Pressure Main Pipe Burst on Cameroon St",
                "description": "Pressurized water gushing from street valve cover, flooding pavement and roadway.",
                "citizen": citizen,
                "citizen_name": citizen.get_full_name() or "Abebe Bikila",
                "citizen_contact": citizen.phone_number or "+251911223344",
                "category": water_cat,
                "department": water_dept,
                "asset": asset_map.get("AST-WTR-001"),
                "latitude": 8.9980,
                "longitude": 38.7840,
                "address": "Cameroon Street, Bole, Addis Ababa",
                "landmark": "Near Medhanialem Mall",
                "priority": ReportPriority.CRITICAL,
                "status": ReportStatus.RESOLVED,
                "resolution_notes": "Valve gland packing replaced and main flange welded. Pressure test passed at 8 bar. Eng. Helen.",
                "resolved_at": now - timedelta(days=1),
                "media_photos": ["/media/reports/demo_water_burst.jpg"],
            }
        )

        Task.objects.update_or_create(
            task_code="TSK-2026-DEMO-003",
            defaults={
                "report": rep3,
                "department": water_dept,
                "assigned_worker": water_contractor,
                "priority": TaskPriority.CRITICAL,
                "status": TaskStatus.RESOLVED,
                "work_description": "Emergency isolation, dewatering, and replacement of 250mm ductile iron pipe sleeve.",
                "internal_note": "Critical commercial sector. Isolate sector valve 12B before cutting.",
                "progress_percentage": 100,
                "original_deadline_date": now - timedelta(days=2),
                "deadline_date": now - timedelta(days=1),
                "resolved_at": now - timedelta(days=1),
                "progress_notes": [
                    {
                        "timestamp": (now - timedelta(days=2)).isoformat(),
                        "author": "Blue Nile Utilities Lead",
                        "note": "Excavation and dewatering complete. Defective pipe joint removed.",
                        "percentage": 60,
                    },
                    {
                        "timestamp": (now - timedelta(days=1)).isoformat(),
                        "author": "Blue Nile Utilities Lead",
                        "note": "Replacement joint installed. Hydrostatic test successful.",
                        "percentage": 100,
                    },
                ],
                "completion_submission": {
                    "completion_date": (now - timedelta(days=1)).isoformat(),
                    "completion_notes": "Repairs tested and certified. Road trench backfilled and sealed.",
                    "before_photos": ["/media/reports/demo_water_burst.jpg"],
                    "after_photos": ["/media/tasks/demo_pipe_repaired.jpg"],
                    "submitted_by": "Blue Nile Utilities Lead",
                },
            }
        )

        # Scenario 4: Streetlight Failure -> RETURNED (Demonstrating substandard rework return)
        rep4, _ = Report.objects.update_or_create(
            report_code="REP-2026-DEMO-004",
            defaults={
                "title": "Streetlights dark across Gotera Interchange",
                "description": "Entire high-mast array off during night hours creating extreme hazard for motorists.",
                "citizen": citizen,
                "citizen_name": citizen.get_full_name() or "Abebe Bikila",
                "citizen_contact": citizen.phone_number or "+251911223344",
                "category": lite_cat,
                "department": lite_dept,
                "asset": asset_map.get("AST-LITE-001"),
                "latitude": 8.9880,
                "longitude": 38.7490,
                "address": "Gotera Interchange South Approach",
                "landmark": "Gotera Flyover",
                "priority": ReportPriority.HIGH,
                "status": ReportStatus.IN_PROGRESS,
                "media_photos": ["/media/reports/demo_dark_street.jpg"],
            }
        )

        Task.objects.update_or_create(
            task_code="TSK-2026-DEMO-004",
            defaults={
                "report": rep4,
                "department": lite_dept,
                "assigned_worker": lite_staff,
                "priority": TaskPriority.HIGH,
                "status": TaskStatus.RETURNED,
                "work_description": "Inspect contactor panel, test 3-phase supply, and replace burnt photocell controller.",
                "internal_note": "Bucket truck required for upper luminaire maintenance.",
                "progress_percentage": 70,
                "original_deadline_date": now + timedelta(days=1),
                "deadline_date": now + timedelta(days=4),
                "rejection_history": [
                    {
                        "timestamp": (now - timedelta(hours=6)).isoformat(),
                        "rejected_by": "Eng. Ermias Lighting Inspector",
                        "reason": "Photocell wired in reverse; fixtures remained on during day and failed to trigger at dusk.",
                        "required_correction": "Rewire controller relay and perform 24h photocell sensor bench test.",
                        "new_expected_date": (now + timedelta(days=4)).isoformat(),
                    }
                ],
            }
        )

        # Scenario 5: Blocked Storm Drain -> NEW (Unassigned, ready for live Admin triage)
        Report.objects.update_or_create(
            report_code="REP-2026-DEMO-005",
            defaults={
                "title": "Blocked Storm Drain causing street flooding in Kality",
                "description": "Culvert clogged with silt and debris; rain runoff flooding industrial access road.",
                "citizen": citizen,
                "citizen_name": citizen.get_full_name() or "Abebe Bikila",
                "citizen_contact": citizen.phone_number or "+251911223344",
                "category": drain_cat,
                "department": drain_dept,
                "asset": asset_map.get("AST-DRN-001"),
                "latitude": 8.9150,
                "longitude": 38.7600,
                "address": "Kality Industrial Road 4",
                "landmark": "Near Kality Depot",
                "priority": ReportPriority.HIGH,
                "status": ReportStatus.NEW,
                "media_photos": ["/media/reports/demo_drain_blocked.jpg"],
                "ai_category_prediction": {"suggested_category": "drainage", "confidence": 0.94},
            }
        )

        # Scenario 6: Waste Overflow -> NEW (Unassigned, ready for live Admin triage)
        Report.objects.update_or_create(
            report_code="REP-2026-DEMO-006",
            defaults={
                "title": "Overflowing Public Waste Bin at Merkato Bus Stand",
                "description": "Bulk refuse accumulating outside bin onto pedestrian walkway creating sanitation hazard.",
                "citizen": citizen,
                "citizen_name": citizen.get_full_name() or "Abebe Bikila",
                "citizen_contact": citizen.phone_number or "+251911223344",
                "category": waste_cat,
                "department": waste_dept,
                "latitude": 9.0300,
                "longitude": 38.7400,
                "address": "Merkato Bus Station Area",
                "landmark": "Near Merkato Main Gate",
                "priority": ReportPriority.MEDIUM,
                "status": ReportStatus.NEW,
                "media_photos": ["/media/reports/demo_waste_overflow.jpg"],
                "ai_category_prediction": {"suggested_category": "garbage", "confidence": 0.98},
            }
        )

        self.stdout.write(
            self.style.SUCCESS(
                "Successfully seeded demo activity: "
                "5 physical assets, 6 realistic reports (across NEW, IN_PROGRESS, COMPLETED_PENDING_VERIFICATION, and RESOLVED), "
                "4 operational tasks, and 1 pending deadline extension."
            )
        )
