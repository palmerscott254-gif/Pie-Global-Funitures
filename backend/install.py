#!/usr/bin/env python
"""
Automated installation script for Pie Global Furniture backend.
Ensures proper dependency installation order for Python 3.11+ compatibility.
"""
import subprocess
import sys
import os


def run_command(command, description):
    """Run a command and handle errors."""
    print(f"\n{'='*60}")
    print(f"▶ {description}")
    print(f"{'='*60}\n")
    
    try:
        result = subprocess.run(
            command,
            shell=True,
            check=True,
            capture_output=True,
            text=True
        )
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        print(f"Output: {e.stdout}")
        print(f"Error: {e.stderr}")
        return False


def main():
    """Main installation process."""
    print("\n" + "="*60)
    print("🚀 Pie Global Furniture Backend Installation")
    print("="*60)
    
    # Check Python version
    print(f"\n📌 Python Version: {sys.version}")
    if sys.version_info < (3, 11):
        print("⚠️  Warning: Python 3.11+ is recommended for best compatibility")
    
    # Step 1: Upgrade pip, setuptools, and wheel
    if not run_command(
        f"{sys.executable} -m pip install --upgrade pip setuptools>=65.0.0 wheel>=0.38.0",
        "Step 1: Upgrading pip, setuptools, and wheel"
    ):
        print("\n❌ Failed to upgrade build tools. Exiting.")
        return False
    
    # Step 2: Install core Django dependencies first
    if not run_command(
        f"{sys.executable} -m pip install Django==5.0.0 djangorestframework==3.14.0",
        "Step 2: Installing core Django packages"
    ):
        print("\n⚠️  Warning: Core Django installation had issues")
    
    # Step 3: Install all dependencies from requirements.txt
    requirements_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    if not run_command(
        f"{sys.executable} -m pip install -r {requirements_path}",
        "Step 3: Installing all dependencies"
    ):
        print("\n❌ Failed to install dependencies. Please check the error messages above.")
        return False
    
    print("\n" + "="*60)
    print("✅ Installation Complete!")
    print("="*60)
    print("\n📋 Next Steps:")
    print("   1. Set up your .env file (copy from .env.example)")
    print("   2. Run migrations: python manage.py migrate")
    print("   3. Create superuser: python manage.py createsuperuser")
    print("   4. Start server: python manage.py runserver")
    print("\n")
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
