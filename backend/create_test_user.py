import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings.base')
django.setup()

from apps.users.models import User

# Create test user
email = 'test@cirp.com'
password = 'test123'

# Check if user exists
if User.objects.filter(email=email).exists():
    user = User.objects.get(email=email)
    user.set_password(password)
    user.save()
    print(f"✅ User {email} password updated to: {password}")
else:
    user = User.objects.create_user(
        email=email,
        password=password,
        first_name='Test',
        last_name='User',
        phone_number='+251911234567'
    )
    print(f"✅ Created new user: {email}")
    print(f"   Password: {password}")

print(f"\n📱 Login Credentials:")
print(f"   Email: {email}")
print(f"   Password: {password}")
