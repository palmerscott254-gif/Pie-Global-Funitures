# Troubleshooting Guide - Python Dependencies

## Common Installation Issues

### Issue 1: Missing `__version__` During Wheel Creation

**Error Message:**
```
AttributeError: module 'pkg_name' has no attribute '__version__'
```

**Root Cause:**
Some older Python packages are not fully compatible with Python 3.11+ and fail during wheel building when setuptools tries to read the `__version__` attribute.

**Solution:**
The `requirements.txt` has been updated to install `setuptools` and `wheel` first, which resolves most compatibility issues.

**Manual Fix:**
```bash
# Install build tools separately
pip install --upgrade pip setuptools>=65.0.0 wheel>=0.38.0

# Then install other dependencies
pip install -r requirements.txt
```

---

### Issue 2: Dependency Conflicts

**Problematic Packages Identified:**
- ✅ `python-decouple==3.8` - Fixed by ensuring latest setuptools
- ✅ All other packages are Python 3.11+ compatible

**Verification:**
All dependencies in `requirements.txt` have been verified for Python 3.11+ compatibility:
- Django 5.0.0 - ✅ Compatible
- djangorestframework 3.14.0 - ✅ Compatible
- django-filter 23.5 - ✅ Compatible
- django-cors-headers 4.3.1 - ✅ Compatible
- psycopg2-binary 2.9.9 - ✅ Compatible
- Pillow 10.2.0 - ✅ Compatible
- python-decouple 3.8 - ✅ Compatible with proper setuptools
- django-ratelimit 4.1.0 - ✅ Compatible
- gunicorn 21.2.0 - ✅ Compatible
- whitenoise 6.6.0 - ✅ Compatible
- django-extensions 3.2.3 - ✅ Compatible

---

### Issue 3: Installation Order Matters

**Problem:**
Installing all dependencies at once may fail if build tools are outdated.

**Solution:**
Use the automated installation scripts which install dependencies in the correct order:
1. Upgrade pip, setuptools, wheel
2. Install core Django packages
3. Install remaining dependencies

---

### Issue 4: Platform-Specific Issues

#### Windows
- Usually no issues with the provided packages
- Use `install.bat` for automated setup

#### Linux/macOS
**psycopg2-binary requirements:**
```bash
# Debian/Ubuntu
sudo apt-get install libpq-dev python3-dev

# macOS
brew install postgresql
```

**Pillow requirements:**
```bash
# Debian/Ubuntu
sudo apt-get install libjpeg-dev zlib1g-dev

# macOS
brew install libjpeg
```

---

### Issue 5: Virtual Environment Issues

**Problem:**
Dependencies installed globally conflict with project requirements.

**Solution:**
Always use a virtual environment:
```bash
# Create new virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Verify you're in the virtual environment
which python  # Should show path inside venv folder
```

---

## Quick Fixes

### Clear pip cache and reinstall:
```bash
pip cache purge
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt --no-cache-dir
```

### Force reinstall of problematic package:
```bash
pip install --force-reinstall --no-cache-dir python-decouple==3.8
```

### Check installed versions:
```bash
pip list
pip show python-decouple
```

---

## Verification Steps

After successful installation, verify:

```bash
# Check Python version
python --version  # Should be 3.11+

# Check if Django is installed
python -c "import django; print(django.get_version())"

# Check all imports
python manage.py check
```

---

## Contact & Support

If issues persist:
1. Check the full error message
2. Verify Python version: `python --version`
3. Ensure virtual environment is activated
4. Try the automated installation scripts
5. Check INSTALL.md for detailed instructions

---

## Prevention

To avoid future issues:
- ✅ Always upgrade pip/setuptools before installing dependencies
- ✅ Use virtual environments
- ✅ Pin dependency versions in requirements.txt
- ✅ Test installations on clean environments
- ✅ Keep setuptools and wheel up to date
