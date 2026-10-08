"""
Create default admin users for CIRP system
Run with: python create_admin_users.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings.base')
django.setup()

from apps.users.models import User
from utils.enums import UserRole

# Admin users to create
admin_users = [
    {
        'email': 'superadmin@cirp.com',
        'password': 'Super@123',
        'first_name': 'Super',
        'last_name': 'Administrator',
        'phone_number': '+251911000001',
        'role': UserRole.SUPER_ADMIN,
    },
    {
        'email': 'roadadmin@cirp.com',
        'password': 'Road@123',
        'first_name': 'Road',
        'last_name': 'Admin',
        'phone_number': '+251911000002',
        'role': UserRole.ROAD_ADMIN,
    },
    {
        'email': 'wateradmin@cirp.com',
        'password': 'Water@123',
        'first_name': 'Water',
        'last_name': 'Admin',
        'phone_number': '+251911000003',
        'role': UserRole.WATER_ADMIN,
    },
    {
        'email': 'electricityadmin@cirp.com',
        'password': 'Electricity@123',
        'first_name': 'Electricity',
        'last_name': 'Admin',
        'phone_number': '+251911000004',
        'role': UserRole.ELECTRICITY_ADMIN,
    },
    {
        'email': 'drainageadmin@cirp.com',
        'password': 'Drainage@123',
        'first_name': 'Drainage',
        'last_name': 'Admin',
        'phone_number': '+251911000005',
        'role': UserRole.DRAINAGE_ADMIN,
    },
    {
        'email': 'wasteadmin@cirp.com',
        'password': 'Waste@123',
        'first_name': 'Waste',
        'last_name': 'Admin',
        'phone_number': '+251911000006',
        'role': UserRole.WASTE_ADMIN,
    },
    {
        'email': 'streetlightadmin@cirp.com',
        'password': 'Light@123',
        'first_name': 'Street Light',
        'last_name': 'Admin',
        'phone_number': '+251911000007',
        'role': UserRole.STREETLIGHT_ADMIN,
    },
    {
        'email': 'facilitiesadmin@cirp.com',
        'password': 'Facilities@123',
        'first_name': 'Public Facilities',
        'last_name': 'Admin',
        'phone_number': '+251911000008',
        'role': UserRole.PUBLIC_FACILITIES_ADMIN,
    },
]

print("=" * 80)
print("CREATING CIRP ADMIN USERS")
print("=" * 80)

for user_data in admin_users:
    email = user_data['email']
    
    # Check if user already exists
    if User.objects.filter(email=email).exists():
        user = User.objects.get(email=email)
        # Update password
        user.set_password(user_data['password'])
        user.role = user_data['role']
        user.first_name = user_data['first_name']
        user.last_name = user_data['last_name']
        user.is_active = True
        user.is_verified = True
        user.save()
        print(f"✅ Updated: {email}")
    else:
        # Create new user
        user = User.objects.create_user(
            email=user_data['email'],
            password=user_data['password'],
            first_name=user_data['first_name'],
            last_name=user_data['last_name'],
            phone_number=user_data['phone_number'],
            role=user_data['role'],
        )
        user.is_verified = True
        user.save()
        print(f"✅ Created: {email}")

print("\n" + "=" * 80)
print("ADMIN CREDENTIALS")
print("=" * 80)
print()
print("┌─────────────────────────────┬────────────────────────────┬─────────────────┐")
print("│ Role                        │ Email                      │ Password        │")
print("├─────────────────────────────┼────────────────────────────┼─────────────────┤")
for user_data in admin_users:
    role = user_data['role'].replace('_', ' ').title()
    email = user_data['email']
    password = user_data['password']
    print(f"│ {role:27s} │ {email:26s} │ {password:15s} │")
print("└─────────────────────────────┴────────────────────────────┴─────────────────┘")
print()
print("🎉 All admin users created successfully!")
print("🌐 Login at: http://localhost:3000")
print()
