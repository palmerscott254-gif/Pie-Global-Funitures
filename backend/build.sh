#!/usr/bin/env bash
set -o errexit
set -o pipefail
set -o nounset

echo "[build] Python: $(python --version)"
echo "[build] Upgrading pip"
python -m pip install --upgrade pip

echo "[build] Installing dependencies from requirements.txt"
pip install -r requirements.txt

echo "[build] Collecting static files"
python manage.py collectstatic --no-input

echo "[build] Build steps completed."
#!/usr/bin/env bash
# exit on error
set -o errexit

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --no-input

# Run migrations
python manage.py migrate --no-input

# Create superuser if it doesn't exist (optional)
# python manage.py shell << END
# from django.contrib.auth import get_user_model
# User = get_user_model()
# if not User.objects.filter(username='admin').exists():
#     User.objects.create_superuser('admin', 'admin@example.com', 'changeme')
# END

echo "Build completed successfully!"
