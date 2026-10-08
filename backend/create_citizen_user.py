#!/usr/bin/env python
"""Create a test citizen user for mobile app"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings.base')
django.setup()

from apps.users.models import User

# Create citizen user
email = "citizen@test.com"
password = "Test@123"

user, created = User.objects.get_or_create(
    email=email,
    defaults={
        'first_name': 'John',
        'last_name': 'Citizen',
        'phone_number': '+1234567890',
        'role': 'CITIZEN',
        'is_active': True,
    }
)

if created:
    user.set_password(password)
    user.save()
    print(f"✅ Created new citizen user!")
else:
    user.set_password(password)
    user.save()
    print(f"✅ Updated existing citizen user!")

print(f"\n📱 MOBILE APP LOGIN CREDENTIALS:")
print(f"Email: {email}")
print(f"Password: {password}")
print(f"Role: {user.role}")
print(f"Name: {user.first_name} {user.last_name}")
