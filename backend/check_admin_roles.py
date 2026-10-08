import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings.local')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

emails = [
    'superadmin@cirp.com',
    'roadadmin@cirp.com',
    'wateradmin@cirp.com',
    'electricityadmin@cirp.com',
    'drainageadmin@cirp.com',
    'wasteadmin@cirp.com',
    'streetlightadmin@cirp.com',
    'facilitiesadmin@cirp.com'
]

print("\n" + "="*80)
print("ADMIN USERS - ROLES AND CREDENTIALS")
print("="*80)
print(f"{'Email':<40} {'Role':<30} {'Department':<20}")
print("-"*80)

for email in emails:
    try:
        user = User.objects.get(email=email)
        dept_name = user.department.name if user.department else "None"
        print(f"{email:<40} {user.role:<30} {dept_name:<20}")
    except User.DoesNotExist:
        print(f"{email:<40} {'USER NOT FOUND':<30} {'-':<20}")

print("="*80)
print("\nPASSWORDS:")
print("-"*80)
print("Super Admin: Super@123")
print("Road Admin: Road@123")
print("Water Admin: Water@123")
print("Electricity Admin: Electricity@123")
print("Drainage Admin: Drainage@123")
print("Waste Admin: Waste@123")
print("Street Light Admin: Light@123")
print("Facilities Admin: Facilities@123")
print("="*80)
