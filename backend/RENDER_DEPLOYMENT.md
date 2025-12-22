# Render Deployment Guide for Pie Global Furniture

## Overview
This guide walks you through deploying the Django backend to Render with PostgreSQL database.

---

## Prerequisites
1. A Render account (sign up at https://render.com)
2. Your GitHub repository connected to Render
3. Environment variables prepared

---

## Step 1: Create PostgreSQL Database

1. **Go to Render Dashboard** → Click "New +" → Select "PostgreSQL"
2. **Configure Database:**
   - **Name:** `pie-global-db`
   - **Database:** `pie_global_db`
   - **User:** `pie_global_user`
   - **Region:** Choose closest to your users (e.g., Oregon)
   - **PostgreSQL Version:** 15 or 16
   - **Plan:** Free or Starter

3. **Save the Database URL:** After creation, copy the "Internal Database URL" from the database dashboard

---

## Step 2: Create Web Service

1. **Go to Render Dashboard** → Click "New +" → Select "Web Service"
2. **Connect Repository:** Link your GitHub repository
3. **Configure Service:**

### Basic Settings:
- **Name:** `pie-global-backend`
- **Region:** Same as database (Oregon)
- **Branch:** `main` (or your default branch)
- **Root Directory:** `backend`
- **Environment:** `Python 3`
- **Build Command:** `./build.sh`
- **Start Command:** `gunicorn pie_global.wsgi:application`

### Advanced Settings:
- **Python Version:** 3.12.0
- **Plan:** Free or Starter ($7/month for always-on)
- **Health Check Path:** `/api/health/`

---

## Step 3: Set Environment Variables

In the Render Web Service dashboard, go to "Environment" tab and add:

### Required Variables:

```bash
# Django Secret Key (generate a strong random key)
DJANGO_SECRET_KEY=your-super-secret-key-here-at-least-50-chars-long

# Debug mode (MUST be False in production)
DJANGO_DEBUG=False

# Allowed hosts (add your Render URL)
DJANGO_ALLOWED_HOSTS=your-app-name.onrender.com

# Database URL (from your PostgreSQL database)
DATABASE_URL=postgresql://user:password@host:port/dbname

# Backend URL (your Render app URL)
BACKEND_URL=https://your-app-name.onrender.com

# CORS Origins (your frontend URLs)
CORS_ALLOWED_ORIGINS=https://your-frontend.vercel.app,https://yourdomain.com
CORS_ALLOW_ALL_ORIGINS=False
```

### Optional Email Variables:

```bash
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=pieglobal308@gmail.com
EMAIL_HOST_PASSWORD=your-gmail-app-password
DEFAULT_FROM_EMAIL=pieglobal308@gmail.com
```

---

## Step 4: Generate Django Secret Key

Run this command locally to generate a secure secret key:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Copy the output and use it for `DJANGO_SECRET_KEY`

---

## Step 5: Deploy

1. Click **"Manual Deploy"** or push to your GitHub branch
2. Watch the build logs for any errors
3. Once deployed, visit: `https://your-app-name.onrender.com/api/health/`
4. You should see: `{"status": "healthy", "service": "pie-global-backend"}`

---

## Step 6: Create Admin User

After successful deployment, use Render Shell:

1. Go to your Web Service dashboard
2. Click **"Shell"** tab
3. Run:
```bash
python manage.py createsuperuser
```
4. Follow prompts to create admin account

---

## Step 7: Configure Static Files

Static files are handled by WhiteNoise (already configured). After deployment:

1. Check that static files are collected: `/staticfiles/` directory
2. Admin panel should have proper CSS: `https://your-app-name.onrender.com/admin/`

---

## Step 8: Media Files (Important!)

**Important:** Render's free tier doesn't persist uploaded files after redeployment.

### Options for Media Files:

#### Option 1: Cloudinary (Recommended)
```bash
# Install packages
pip install django-cloudinary-storage cloudinary

# Add to requirements.txt
django-cloudinary-storage==0.3.0
cloudinary==1.36.0

# Environment variables
CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-api-key
CLOUDINARY_API_SECRET=your-api-secret
```

Update `settings.py`:
```python
INSTALLED_APPS = [
    # ...
    'cloudinary_storage',
    'cloudinary',
    # ...
]

CLOUDINARY_STORAGE = {
    'CLOUD_NAME': config('CLOUDINARY_CLOUD_NAME'),
    'API_KEY': config('CLOUDINARY_API_KEY'),
    'API_SECRET': config('CLOUDINARY_API_SECRET'),
}

DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
```

#### Option 2: AWS S3
Use `django-storages` with S3 bucket

#### Option 3: Render Disk (Paid plans only)
Add persistent disk in Render dashboard

---

## Step 9: Update Frontend

Update your frontend's API base URL to point to Render:

```typescript
// In frontend/src/services/api.ts
const API_BASE_URL = 'https://your-app-name.onrender.com/api';
```

---

## Troubleshooting

### Build Fails
- Check `build.sh` has execute permissions
- Verify all dependencies in `requirements.txt`
- Check build logs for specific errors

### Database Connection Issues
- Verify `DATABASE_URL` is correct
- Check database is in same region as web service
- Ensure PostgreSQL version compatibility

### Static Files Not Loading
- Run `python manage.py collectstatic` manually in Render Shell
- Check `STATIC_ROOT` and `STATIC_URL` settings
- Verify WhiteNoise is in `MIDDLEWARE`

### CORS Errors
- Add frontend URL to `CORS_ALLOWED_ORIGINS`
- Ensure URL format is correct (no trailing slash)
- Check `CORS_ALLOW_CREDENTIALS` setting

### 502 Bad Gateway
- Check if migrations ran successfully
- Verify gunicorn is starting correctly
- Check application logs in Render dashboard

### Media Files Not Persisting
- This is expected on free tier
- Set up Cloudinary or upgrade to paid plan with disk

---

## Monitoring & Maintenance

### View Logs
- Go to Render Dashboard → Your Service → Logs tab
- Filter by errors: Look for 500 errors

### Database Backups
- Render automatically backs up databases
- Manual backup: Dashboard → Database → Backups

### Update Deployment
- Push to GitHub → Auto-deploys (if enabled)
- Or click "Manual Deploy" in Render dashboard

---

## Environment Variables Checklist

✅ DJANGO_SECRET_KEY (generated securely)
✅ DJANGO_DEBUG (set to False)
✅ DJANGO_ALLOWED_HOSTS (your Render URL)
✅ DATABASE_URL (from Render PostgreSQL)
✅ BACKEND_URL (your Render app URL)
✅ CORS_ALLOWED_ORIGINS (frontend URLs)
✅ CORS_ALLOW_ALL_ORIGINS (set to False)
□ Email settings (optional)
□ Cloudinary settings (if using)

---

## Useful Commands (Render Shell)

```bash
# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic --no-input

# Check deployment
python manage.py check --deploy

# Open Django shell
python manage.py shell
```

---

## Cost Estimates

### Free Tier (Good for testing):
- Web Service: Free (spins down after 15 min inactivity)
- PostgreSQL: Free (90 days, then $7/month)

### Production Ready:
- Web Service: $7/month (Starter - always on)
- PostgreSQL: $7/month (Starter - 256MB RAM)
- **Total: ~$14/month**

### With More Resources:
- Web Service: $25/month (Standard)
- PostgreSQL: $20/month (Standard - 1GB RAM)
- **Total: ~$45/month**

---

## Security Checklist

✅ `DEBUG = False` in production
✅ Strong `SECRET_KEY` (50+ characters)
✅ HTTPS enforced (automatic on Render)
✅ `ALLOWED_HOSTS` properly configured
✅ CORS restricted to known origins
✅ Database credentials secured
✅ Email credentials (if used) secured
✅ Admin URL not exposed publicly (optional: change to custom URL)

---

## Next Steps

1. ✅ Deploy backend to Render
2. ✅ Set up PostgreSQL database
3. ✅ Configure environment variables
4. ✅ Test API endpoints
5. ✅ Create admin user
6. Deploy frontend (Vercel/Netlify)
7. Set up Cloudinary for media files
8. Configure custom domain (optional)
9. Set up monitoring/alerts
10. Plan backup strategy

---

## Support & Resources

- **Render Docs:** https://render.com/docs
- **Django on Render:** https://render.com/docs/deploy-django
- **PostgreSQL on Render:** https://render.com/docs/databases
- **Cloudinary:** https://cloudinary.com/documentation/django_integration

---

## Questions?

Common issues and solutions are in the Troubleshooting section above. For Render-specific issues, check:
- Render Dashboard Logs
- Render Community: https://community.render.com
- Render Status: https://status.render.com
