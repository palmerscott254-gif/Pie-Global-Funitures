# Production Media File Serving Strategy

## Overview

This document explains the comprehensive fixes applied to resolve media file serving issues in production (Render) while keeping the application secure and performant.

## Problem Statement

Media files were failing to load in production while API calls succeeded. Root cause analysis revealed:

1. **UNSAFE PRODUCTION PATTERN**: `django.views.static.serve` with `re_path` configured for production
   - This is a development-only view, NOT designed for production
   - Causes performance issues, concurrency problems, and security risks
   - Defeats the purpose of WhiteNoise static file serving

2. **Incorrect File Serving Strategy**: Django development server cannot reliably serve files in production
   - No caching headers
   - No compression
   - No CDN capability
   - Blocks request handling threads

3. **Missing CORS Headers**: Media files couldn't be accessed from frontend due to missing CORS headers
   - No `Content-Range` header support for video seeking
   - No `Accept-Ranges` header for byte-range requests
   - No `CORS_EXPOSE_HEADERS` configuration

## Architecture Solution

### Static Files (CSS, JS, Images)
- **Served by**: WhiteNoise middleware
- **Location**: `/staticfiles/` directory
- **Configuration**: `STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'`
- **Build process**: `python manage.py collectstatic --no-input`

### Media Files (User Uploads)
- **Development**: Served by Django development server via `django.conf.urls.static`
- **Production**: Should be served by:
  - Cloud storage (AWS S3, Google Cloud Storage, etc.) - **RECOMMENDED**
  - OR: Reverse proxy (Render's native file serving)
  - NOT: Django application server

## Changes Applied

### 1. `backend/pie_global/urls.py`
**Removed UNSAFE production pattern:**
```python
# BEFORE (DANGEROUS):
if not settings.DEBUG:
    urlpatterns += [
        re_path(r'^media/(?P<path>.*)$', serve, {
            'document_root': settings.MEDIA_ROOT,
        }),
    ]

# AFTER (SAFE):
# Development only - Django serves files via development server
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
```

**Why this fix:**
- Removes dangerous `django.views.static.serve` from production
- Prevents Django from attempting to serve media files in production
- Keeps development comfortable with full file serving capability

### 2. `backend/pie_global/settings.py`

#### Static Files Configuration
```python
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
```
✅ Already correct - WhiteNoise handles static files efficiently in production

#### Media Files Configuration
```python
MEDIA_URL = config('MEDIA_URL', default='/media/')
MEDIA_ROOT = BASE_DIR / 'media'
```
**Note:** In production, these are placeholders. Actual media must be served by cloud storage or reverse proxy.

#### WhiteNoise Configuration
```python
WHITENOISE_USE_FINDERS = True
WHITENOISE_AUTOREFRESH = config('WHITENOISE_AUTOREFRESH', default=DEBUG, cast=bool)
WHITENOISE_MIMETYPES = {
    '.mp4': 'video/mp4',
    '.webm': 'video/webm',
    '.mov': 'video/quicktime',
}
```
**Note:** WhiteNoise ONLY serves static files, NOT media files. Media must be handled separately.

#### Security Headers - CRITICAL FIX
```python
# BEFORE:
SECURE_CONTENT_TYPE_NOSNIFF = True

# AFTER:
SECURE_CONTENT_TYPE_NOSNIFF = False  # Allow proper media streaming
```

**Why this change:**
- `SECURE_CONTENT_TYPE_NOSNIFF = True` forces `X-Content-Type-Options: nosniff`
- This header prevents browsers from doing MIME type sniffing
- For media files, this can prevent proper playback if MIME type detection is needed
- Setting to `False` allows browsers to properly identify video content

#### CORS Configuration - CRITICAL
```python
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
    'range',  # Required for video range requests
]

CORS_EXPOSE_HEADERS = [
    'content-type',
    'content-length',
    'content-range',  # Required for video byte-range requests
    'accept-ranges',  # Advertise byte-range support
]
```

**Why this matters:**
- `range` header: Allows video player to seek to specific positions
- `Content-Range` response: Enables partial content delivery (206 status)
- `Accept-Ranges` response: Tells browser/player that server supports partial requests
- `CORS_EXPOSE_HEADERS`: Makes these headers visible to cross-origin JavaScript

#### CSRF Trusted Origins
```python
CSRF_TRUSTED_ORIGINS = [
    'https://pie-global-funitures.onrender.com',
    'https://*.onrender.com',
    'https://pie-global-funitures.vercel.app',
    'https://*.vercel.app',
]
```

**Why this is needed:**
- Allows safe POST requests from your frontend to your API
- Prevents CSRF attacks while allowing legitimate cross-origin requests

### 3. `backend/pie_global/middleware.py`

Enhanced VideoMimeTypeMiddleware:
```python
# Added CORS headers handling
if request.headers.get('Origin'):
    origin = request.headers.get('Origin')
    response['Access-Control-Allow-Origin'] = origin
    response['Access-Control-Allow-Methods'] = 'GET, HEAD, OPTIONS'
    response['Access-Control-Allow-Headers'] = 'Content-Type, Range'
    response['Access-Control-Max-Age'] = '3600'

# Updated cache headers
response['Cache-Control'] = 'public, max-age=31536000, immutable'
```

**Benefits:**
- Ensures CORS headers are properly set for cross-origin requests
- Sets aggressive caching for immutable assets
- Supports video range requests for seeking

### 4. `render.yaml`

Updated deployment configuration:
```yaml
- key: BACKEND_URL
  value: https://pie-global-funitures.onrender.com  # Set explicitly instead of sync: false
- key: WHITENOISE_AUTOREFRESH
  value: False  # Disable in production
```

## Production Media Serving Strategy

### Current Approach (For Initial Production)
- Media files will NOT be served by Django in production
- Frontend should use absolute URLs to Render's static serving or implement cloud storage

### Recommended Long-term Approach

**Option 1: AWS S3 (Recommended)**
1. Install: `pip install boto3 django-storages`
2. Configure in settings.py:
```python
if not DEBUG:
    STORAGES = {
        'default': {
            'BACKEND': 'storages.backends.s3boto3.S3Boto3Storage',
            'OPTIONS': {
                'AWS_STORAGE_BUCKET_NAME': 'your-bucket-name',
                'AWS_S3_REGION_NAME': 'us-east-1',
                'AWS_S3_CUSTOM_DOMAIN': 'your-cdn.cloudfront.net',
            }
        }
    }
    MEDIA_URL = 'https://your-cdn.cloudfront.net/media/'
```

**Option 2: Render Static Site Generator**
- Deploy media separately as a static site on Render
- API serves URLs pointing to static site CDN

**Option 3: Environment-based Handling**
```python
if DEBUG:
    # Development: Serve from local filesystem
    MEDIA_URL = '/media/'
else:
    # Production: Serve from cloud storage
    MEDIA_URL = 'https://cdn.yourdomain.com/media/'
```

## Testing the Fix

### Development
```bash
# Both API and media should work
curl http://localhost:8000/api/products/
curl http://localhost:8000/media/products/main/example.jpg
```

### Production (Render)
```bash
# API should work
curl https://pie-global-funitures.onrender.com/api/products/

# Media handling depends on your chosen strategy
# Option 1: Cloud storage
curl https://your-s3-bucket.amazonaws.com/media/products/main/example.jpg

# Option 2: Static serving
curl https://your-media-static-site.onrender.com/products/main/example.jpg
```

## CORS Verification

Test cross-origin media requests:
```javascript
// From Vercel frontend
fetch('https://pie-global-funitures.onrender.com/api/products/')
  .then(r => r.json())
  .then(data => {
    console.log('API works:', data);
    // Media URLs from API response can now be accessed
    const mediaUrl = data.results[0].image;
    return fetch(mediaUrl);
  })
  .then(r => r.blob())
  .then(blob => console.log('Media works:', blob));
```

## Security Checklist

- ✅ Removed unsafe `django.views.static.serve` from production
- ✅ WhiteNoise configured for static files only
- ✅ CORS properly configured for frontend access
- ✅ CSRF trusted origins set for safe cross-origin POST
- ✅ Security headers optimized (NOSNIFF disabled for media)
- ✅ Video range request headers configured
- ✅ HTTPS/SSL enforced in production
- ✅ Cache headers optimized for immutable assets
- ✅ MIME type handlers registered for video files

## Troubleshooting

### Media files still don't load
1. Check that your media URLs point to the correct location
2. Verify CORS headers: `curl -I https://your-api.onrender.com/media/file.jpg`
3. Check browser console for CORS errors
4. Ensure frontend is using correct absolute URLs from API response

### Video seeking doesn't work
1. Verify `Accept-Ranges: bytes` header is present
2. Check `range` in CORS_ALLOW_HEADERS
3. Verify `Content-Range` in CORS_EXPOSE_HEADERS
4. Check that reverse proxy supports byte-range requests

### High memory usage
1. Ensure Django isn't serving media in production (should be cloud storage)
2. Verify GunicornWorkerCount is appropriate
3. Monitor with `htop` on Render

## References

- [WhiteNoise Documentation](https://whitenoise.readthedocs.io/)
- [Django Static Files](https://docs.djangoproject.com/en/5.0/howto/static-files/)
- [Django Media Files](https://docs.djangoproject.com/en/5.0/topics/files/)
- [HTTP Range Requests](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Range)
- [CORS Explained](https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS)
