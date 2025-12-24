"""
Django settings for Pie Global Furniture project.
"""

import os
import dj_database_url
from pathlib import Path
from decouple import config, Csv
from urllib.parse import urlparse

# Build paths
BASE_DIR = Path(__file__).resolve().parent.parent

# Security Settings
SECRET_KEY = config('DJANGO_SECRET_KEY', default='INSECURE-change-me-in-production-use-strong-random-key')
DEBUG = config('DJANGO_DEBUG', default=True, cast=bool)
# Should strip the scheme from ALLOWED_HOSTS
ALLOWED_HOSTS = [
    urlparse(host).netloc if '://' in host else host 
    for host in config('DJANGO_ALLOWED_HOSTS', default='localhost,127.0.0.1,pie-global-funitures.onrender.com,*.onrender.com', cast=Csv())
]

# Application definition
INSTALLED_APPS = [
    # Django core
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third-party
    'rest_framework',
    'corsheaders',
    'django_filters',

    # Local apps
    'apps.products',
    'apps.home',
    'apps.messages.apps.MessagesConfig',
    'apps.orders',
    'apps.about',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Static files
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'pie_global.middleware.VideoMimeTypeMiddleware',  # Video MIME types
]

ROOT_URLCONF = 'pie_global.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'pie_global.wsgi.application'

# Database
# Use DATABASE_URL if available (Render), otherwise use individual settings
DATABASE_URL = os.environ.get('DATABASE_URL', '').strip()

# Try to use dj_database_url if DATABASE_URL is properly set, otherwise fall back to manual config
DATABASES = {}
if DATABASE_URL and '://' in DATABASE_URL:
    try:
        DATABASES = {
            'default': dj_database_url.config(
                default=DATABASE_URL,
                conn_max_age=600,
                conn_health_checks=True,
            )
        }
    except ValueError:
        # If parsing fails (e.g., empty URL), use manual config
        DATABASES = {}

# Fall back to SQLite during build if DATABASE_URL is missing/invalid
# Render sets DATABASE_URL at runtime; builds (collectstatic) can run without Postgres
if not DATABASES:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization
# No trailing whitespace in this docstring or in this file
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
# WhiteNoise serves these from STATIC_ROOT during production
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Media files (User uploads)
# IMPORTANT: In production, these must be served by a cloud storage provider (AWS S3, etc.)
# or through a reverse proxy. Django should NOT serve these directly.
# For now, configure them for local development and cloud storage integration
MEDIA_URL = config('MEDIA_URL', default='/media/')
MEDIA_ROOT = BASE_DIR / 'media'

# WhiteNoise Configuration for Static Files
# WhiteNoise ONLY serves static files, not media files
# Media files must be handled separately (cloud storage recommended for production)
WHITENOISE_USE_FINDERS = True
WHITENOISE_AUTOREFRESH = config('WHITENOISE_AUTOREFRESH', default=DEBUG, cast=bool)
WHITENOISE_MIMETYPES = {
    '.mp4': 'video/mp4',
    '.webm': 'video/webm',
    '.mov': 'video/quicktime',
}

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Django REST Framework
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 12,
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour',
    },
}

# CORS Settings
# Configure CORS to allow media and API requests from frontend domains
CORS_ALLOWED_ORIGINS = [
    f"{urlparse(origin).scheme}://{urlparse(origin).netloc}" if '://' in origin else origin
    for origin in config(
        'CORS_ALLOWED_ORIGINS',
        default='http://localhost:3000,http://localhost:5173,https://pie-global-funitures.vercel.app',
        cast=Csv()
    )
]

# Allow Vercel preview deployments (e.g., *-palmerscott254-gifs-projects.vercel.app)
# This enables previews from any Vercel preview branch
CORS_ALLOWED_ORIGIN_REGEXES = [
    r'^https://.*\.vercel\.app$',  # Matches all Vercel preview URLs
]

CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_ALL_ORIGINS = config('CORS_ALLOW_ALL_ORIGINS', default=False, cast=bool)

# CORS Headers - IMPORTANT for media file requests
# These headers are needed for cross-origin media file access and proper streaming
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
    'range',  # Required for video range requests (seeking)
]

# CORS Expose Headers - Necessary for media file operations
CORS_EXPOSE_HEADERS = [
    'content-type',
    'content-length',
    'content-range',  # Required for video streaming byte-range requests
    'accept-ranges',  # Advertise support for range requests
    'access-control-allow-origin',
]

# Security settings for production
# NOTE: These settings enforce HTTPS and security best practices
# IMPORTANT: Ensure your reverse proxy (Render) is properly configured
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    # Allow Content-Type detection for media files (needed for video/file streaming)
    SECURE_CONTENT_TYPE_NOSNIFF = False  # Changed from True to allow proper media streaming
    X_FRAME_OPTIONS = 'DENY'
    # Allow same-origin frames for embedded media
    CSRF_TRUSTED_ORIGINS = [
        'https://pie-global-funitures.onrender.com',
        'https://*.onrender.com',
        'https://pie-global-funitures.vercel.app',
        'https://*.vercel.app',
    ]

# File Upload Settings
FILE_UPLOAD_MAX_MEMORY_SIZE = 10485760  # 10MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 10485760  # 10MB
ALLOWED_IMAGE_EXTENSIONS = ['jpg', 'jpeg', 'png', 'webp', 'svg']
ALLOWED_VIDEO_EXTENSIONS = ['mp4', 'webm', 'mov']

# Email Configuration (optional)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = True
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='pieglobal308@gmail.com')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='pieglobal308@gmail.com')

# Logging
LOG_FILE_PATH = BASE_DIR / 'logs' / 'django.log'
# Try to ensure the logs directory exists; if it fails (e.g., read-only during build), fall back to console-only
try:
    LOG_FILE_PATH.parent.mkdir(parents=True, exist_ok=True)
    log_file_available = True
except Exception:
    log_file_available = False

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        # Only register file handler if the log path is available to avoid startup failure on platforms like Render build step
        **({
            'file': {
                'class': 'logging.FileHandler',
                'filename': LOG_FILE_PATH,
                'formatter': 'verbose',
            }
        } if log_file_available else {}),
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'] if (not DEBUG and log_file_available) else ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
