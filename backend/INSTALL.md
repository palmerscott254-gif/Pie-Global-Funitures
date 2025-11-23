# Installation Instructions for Backend

## Quick Start

### 1. Upgrade pip, setuptools, and wheel first:
```bash
python -m pip install --upgrade pip setuptools wheel
```

### 2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Troubleshooting

### If you encounter "__version__" errors during installation:

**Problem:** Some older packages may fail during wheel building with Python 3.11+

**Solution:** The requirements.txt has been updated to ensure setuptools and wheel are installed first.

### Alternative Installation (if issues persist):

```bash
# Install build tools separately
pip install --upgrade pip setuptools>=65.0.0 wheel>=0.38.0

# Install Django and core dependencies first
pip install Django==5.0.0 djangorestframework==3.14.0

# Install remaining dependencies
pip install -r requirements.txt
```

### Python Version Requirements:
- Python 3.11 or higher recommended
- All dependencies are compatible with Python 3.11+

### Common Issues:

1. **python-decouple**: If version 3.8 causes issues, you can use:
   ```bash
   pip install python-decouple>=3.8,<4.0
   ```

2. **psycopg2-binary**: On some systems, you may need to install system dependencies:
   - **Windows**: No additional dependencies needed
   - **Linux**: `sudo apt-get install libpq-dev python3-dev`
   - **macOS**: `brew install postgresql`

3. **Pillow**: Requires image libraries:
   - **Windows**: Included with binary wheel
   - **Linux**: `sudo apt-get install libjpeg-dev zlib1g-dev`
   - **macOS**: `brew install libjpeg`

## Environment Setup

1. Create a virtual environment:
   ```bash
   python -m venv venv
   ```

2. Activate the virtual environment:
   - **Windows**: `venv\Scripts\activate`
   - **Linux/macOS**: `source venv/bin/activate`

3. Follow installation steps above

4. Run migrations:
   ```bash
   python manage.py migrate
   ```

5. Create superuser:
   ```bash
   python manage.py createsuperuser
   ```

6. Run development server:
   ```bash
   python manage.py runserver
   ```
