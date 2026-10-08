import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings.base')
django.setup()

from apps.users.models import User

try:
    user = User.objects.get(email='test@cirp.com')
    print(f"User found: {user.email}")
    print(f"Name: {user.first_name} {user.last_name}")
    print(f"Phone: {user.phone_number}")
    print(f"Is active: {user.is_active}")
    print(f"Check password 'test123': {user.check_password('test123')}")
except User.DoesNotExist:
    print("User with email 'test@cirp.com' does not exist!")
    print("\nAll users in database:")
    for u in User.objects.all():
        print(f"  - {u.email}")
