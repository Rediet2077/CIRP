#!/usr/bin/env python
"""List all admin users with their roles and credentials"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings.local')
django.setup()

from apps.users.models import User

print("\n" + "="*100)
print("CIRP ADMIN USERS - COMPLETE LIST")
print("="*100)
print(f"{'Email':<40} {'Role':<30} {'Department':<20} {'Password':<15}")
print("-"*100)

admin_users = [
    ('superadmin@cirp.com', 'Super@123'),
    ('roadadmin@cirp.com', 'Road@123'),
    ('wateradmin@cirp.com', 'Water@123'),
    ('electricityadmin@cirp.com', 'Electricity@123'),
    ('drainageadmin@cirp.com', 'Drainage@123'),
    ('wasteadmin@cirp.com', 'Waste@123'),
    ('streetlightadmin@cirp.com', 'Light@123'),
    ('facilitiesadmin@cirp.com', 'Facilities@123'),
]

for email, password in admin_users:
    try:
        user = User.objects.get(email=email)
        dept_name = user.department.name if user.department else "No Department"
        print(f"{email:<40} {user.role:<30} {dept_name:<20} {password:<15}")
    except User.DoesNotExist:
        print(f"{email:<40} {'NOT FOUND':<30} {'-':<20} {password:<15}")

print("="*100)
print("\nEXPECTED BEHAVIOR:")
print("-"*100)
print("✅ Super Admin (SUPER_ADMIN):")
print("   - Should see: Dashboard, Departments, Users, Reports, Assets, Notifications, Settings")
print("   - Full system access")
print("")
print("✅ Department Admins (ROAD_ADMIN, WATER_ADMIN, etc.):")
print("   - Should see: Dashboard, Reports, Assets, Notifications")
print("   - Limited to department scope")
print("="*100)
print("\n🌐 Access URLs:")
print("   - Backend API: http://0.0.0.0:8000")
print("   - Admin Panel: http://localhost:3000")
print("   - Admin Panel (Network): http://192.168.137.1:3000")
print("="*100 + "\n")
