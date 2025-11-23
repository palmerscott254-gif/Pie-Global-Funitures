#!/usr/bin/env python
"""
Test script to verify all dependencies are properly installed.
Run this after installation to check for any issues.
"""
import sys


def test_import(module_name, package_name=None):
    """Test if a module can be imported."""
    try:
        __import__(module_name)
        print(f"✅ {package_name or module_name} - OK")
        return True
    except ImportError as e:
        print(f"❌ {package_name or module_name} - FAILED: {e}")
        return False


def main():
    """Run all dependency tests."""
    print("\n" + "="*60)
    print("🔍 Testing Python Dependencies")
    print("="*60 + "\n")
    
    # Check Python version
    print(f"Python Version: {sys.version}")
    if sys.version_info < (3, 11):
        print("⚠️  Warning: Python 3.11+ is recommended\n")
    else:
        print("✅ Python version is compatible\n")
    
    print("Testing imports...\n")
    
    # Test all critical imports
    tests = [
        ("django", "Django"),
        ("rest_framework", "Django REST Framework"),
        ("django_filters", "django-filter"),
        ("corsheaders", "django-cors-headers"),
        ("psycopg2", "psycopg2-binary"),
        ("PIL", "Pillow"),
        ("decouple", "python-decouple"),
        ("django_ratelimit", "django-ratelimit"),
        ("gunicorn", "gunicorn"),
        ("whitenoise", "whitenoise"),
        ("django_extensions", "django-extensions"),
    ]
    
    results = []
    for module, package in tests:
        results.append(test_import(module, package))
    
    # Summary
    print("\n" + "="*60)
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"✅ All {total} dependencies installed successfully!")
        print("="*60)
        print("\n🎉 You're ready to start development!\n")
        print("Next steps:")
        print("  1. Configure your .env file")
        print("  2. Run: python manage.py migrate")
        print("  3. Run: python manage.py createsuperuser")
        print("  4. Run: python manage.py runserver\n")
        return True
    else:
        print(f"⚠️  {passed}/{total} dependencies installed")
        print("="*60)
        print("\n❌ Some dependencies failed to install")
        print("Please check the errors above and refer to TROUBLESHOOTING.md\n")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
