"""
Pie Global Furniture - E-commerce Platform
Django Backend API

Setup Instructions:
1. Install dependencies: pip install -r requirements.txt
2. Copy .env.example to .env and configure
3. Run migrations: python manage.py migrate
4. Create superuser: python manage.py createsuperuser
5. Run server: python manage.py runserver

API Endpoints:
- /api/products/ - Furniture products
- /api/orders/ - Customer orders
- /api/sliders/ - Homepage slider images
- /api/videos/ - Homepage hero videos
- /api/messages/ - Contact messages
- /api/about/ - About page content
- /admin/ - Django admin panel

For production deployment:
- Set DEBUG=False in .env
- Configure proper SECRET_KEY
- Set up PostgreSQL database
- Configure CORS_ALLOWED_ORIGINS
- Set up media storage (AWS S3 recommended)
- Use gunicorn as WSGI server
"""
