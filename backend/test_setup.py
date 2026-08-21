#!/usr/bin/env python
"""
CIRP Backend - Setup Verification Script
Tests database connectivity, migrations, and basic configuration
"""

import os
import sys
import django
from pathlib import Path

# Add the backend directory to Python path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings.base')
django.setup()

from django.core.management import call_command
from django.db import connection
from django.conf import settings

def test_database_connection():
    """Test PostgreSQL/PostGIS connection"""
    print("\n" + "="*70)
    print("Testing Database Connection...")
    print("="*70)
    
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT version();")
            version = cursor.fetchone()[0]
            print(f"✓ PostgreSQL Connected: {version[:50]}...")
            
            # Check PostGIS extension
            cursor.execute("SELECT PostGIS_version();")
            postgis_version = cursor.fetchone()[0]
            print(f"✓ PostGIS Extension: {postgis_version}")
            
        return True
    except Exception as e:
        print(f"✗ Database Connection Failed: {e}")
        return False

def test_migrations():
    """Check migration status"""
    print("\n" + "="*70)
    print("Checking Migrations...")
    print("="*70)
    
    try:
        # Show migration status
        call_command('showmigrations', '--list')
        print("\n✓ Migrations check completed")
        return True
    except Exception as e:
        print(f"✗ Migration check failed: {e}")
        return False

def test_apps():
    """Test installed apps"""
    print("\n" + "="*70)
    print("Checking Installed Apps...")
    print("="*70)
    
    installed_apps = settings.INSTALLED_APPS
    cirp_apps = [app for app in installed_apps if app.startswith('apps.')]
    
    print(f"\nTotal Django Apps: {len(installed_apps)}")
    print(f"\nCIRP Domain Apps ({len(cirp_apps)}):")
    for app in cirp_apps:
        print(f"  ✓ {app}")
    
    return True

def test_configuration():
    """Test key configuration settings"""
    print("\n" + "="*70)
    print("Checking Configuration...")
    print("="*70)
    
    checks = {
        'DEBUG': settings.DEBUG,
        'SECRET_KEY': 'Configured' if settings.SECRET_KEY != 'django-insecure-default-change-me' else 'Using Default (Change in Production!)',
        'ALLOWED_HOSTS': settings.ALLOWED_HOSTS,
        'DATABASE_ENGINE': settings.DATABASES['default']['ENGINE'],
        'AI_SERVICE_URL': getattr(settings, 'AI_SERVICE_URL', 'Not configured'),
        'CORS_ALLOWED': 'All Origins' if getattr(settings, 'CORS_ALLOW_ALL_ORIGINS', False) else settings.CORS_ALLOWED_ORIGINS,
    }
    
    for key, value in checks.items():
        print(f"  • {key}: {value}")
    
    return True

def run_all_tests():
    """Run all verification tests"""
    print("\n" + "="*70)
    print("CIRP BACKEND - SETUP VERIFICATION")
    print("="*70)
    
    results = []
    
    # Run tests
    results.append(("Database Connection", test_database_connection()))
    results.append(("Configuration", test_configuration()))
    results.append(("Installed Apps", test_apps()))
    results.append(("Migrations", test_migrations()))
    
    # Summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    
    for test_name, passed in results:
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{status}: {test_name}")
    
    all_passed = all(result[1] for result in results)
    
    if all_passed:
        print("\n🎉 All tests passed! Backend is properly configured.")
    else:
        print("\n⚠️  Some tests failed. Please check the errors above.")
    
    return all_passed

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
