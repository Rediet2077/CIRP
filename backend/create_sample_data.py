"""
Create sample data for testing
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings.base')
django.setup()

from apps.categories.models import Category
from apps.departments.models import Department

# Create categories
categories_data = [
    {"name": "Road Damage", "code": "ROAD_DAMAGE", "description": "Potholes, cracks, and road surface issues"},
    {"name": "Street Lighting", "code": "STREET_LIGHT", "description": "Broken or malfunctioning street lights"},
    {"name": "Water Supply", "code": "WATER_SUPPLY", "description": "Water leaks, pipe bursts, or supply issues"},
    {"name": "Drainage", "code": "DRAINAGE", "description": "Blocked drains or flooding issues"},
    {"name": "Waste Management", "code": "WASTE_MGMT", "description": "Overflowing bins or missed collections"},
    {"name": "Parks & Recreation", "code": "PARKS_REC", "description": "Park maintenance and equipment issues"},
    {"name": "Traffic Signals", "code": "TRAFFIC_SIG", "description": "Malfunctioning traffic lights or signs"},
    {"name": "Other", "code": "OTHER", "description": "Other infrastructure issues"},
]

print("Creating categories...")
for cat_data in categories_data:
    category, created = Category.objects.get_or_create(
        code=cat_data["code"],
        defaults={
            "name": cat_data["name"],
            "description": cat_data["description"],
        }
    )
    if created:
        print(f"✓ Created category: {category.name}")
    else:
        print(f"  Category already exists: {category.name}")

# Create departments
departments_data = [
    {
        "name": "Public Works Department",
        "code": "PUBLIC_WORKS",
        "description": "Responsible for roads, bridges, and general infrastructure",
        "email": "publicworks@cirp.com",
        "phone": "555-0100",
    },
    {
        "name": "Water & Sanitation Department",
        "code": "WATER_SANIT",
        "description": "Manages water supply, sewage, and drainage systems",
        "email": "water@cirp.com",
        "phone": "555-0200",
    },
    {
        "name": "Parks & Recreation Department",
        "code": "PARKS_REC",
        "description": "Maintains parks, playgrounds, and recreational facilities",
        "email": "parks@cirp.com",
        "phone": "555-0300",
    },
    {
        "name": "Traffic & Transportation Department",
        "code": "TRAFFIC_TRANS",
        "description": "Manages traffic signals, signage, and public transportation",
        "email": "traffic@cirp.com",
        "phone": "555-0400",
    },
]

print("\nCreating departments...")
for dept_data in departments_data:
    department, created = Department.objects.get_or_create(
        code=dept_data["code"],
        defaults={
            "name": dept_data["name"],
            "description": dept_data["description"],
            "email": dept_data["email"],
            "phone": dept_data["phone"],
        }
    )
    if created:
        print(f"✓ Created department: {department.name}")
    else:
        print(f"  Department already exists: {department.name}")

print("\n✅ Sample data creation complete!")
print(f"Total categories: {Category.objects.count()}")
print(f"Total departments: {Department.objects.count()}")
