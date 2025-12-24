# Render Environment Variables - Quick Reference

## Copy & Paste to Render Dashboard

### 1. Generate Secret Key First
Run locally:
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

---

## Required Environment Variables

| Variable | Value | Notes |
|----------|-------|-------|
| `DJANGO_SECRET_KEY` | `<generated-key>` | Generate using command above |
| `DJANGO_DEBUG` | `False` | MUST be False in production |
| `DJANGO_ALLOWED_HOSTS` | `pie-global-funitures.onrender.com` | Your Render app URL (without https://) |
| `DATABASE_URL` | `<from-render-db>` | Automatically set when you link database |
| `BACKEND_URL` | `https://pie-global-funitures.onrender.com` | Full URL with https:// |
| `CORS_ALLOWED_ORIGINS` | `https://pie-global-funitures.vercel.app` | Your production frontend URL (Vercel previews auto-allowed) |
| `CORS_ALLOW_ALL_ORIGINS` | `False` | Security - keep False in production |

---

## Optional Variables

### Email Configuration (for contact form notifications)
| Variable | Value | Example |
|----------|-------|---------|
| `EMAIL_HOST` | `smtp.gmail.com` | Gmail SMTP |
| `EMAIL_PORT` | `587` | Standard TLS port |
| `EMAIL_HOST_USER` | `pieglobal308@gmail.com` | Your email |
| `EMAIL_HOST_PASSWORD` | `<app-password>` | Gmail app password (not regular password) |
| `DEFAULT_FROM_EMAIL` | `pieglobal308@gmail.com` | From address |

### Media Files (Cloudinary - Recommended)
| Variable | Value | Where to get |
|----------|-------|--------------|
| `CLOUDINARY_CLOUD_NAME` | `<your-cloud-name>` | Cloudinary Dashboard |
| `CLOUDINARY_API_KEY` | `<your-api-key>` | Cloudinary Dashboard |
| `CLOUDINARY_API_SECRET` | `<your-api-secret>` | Cloudinary Dashboard |

---

## Example Setup

### Step 1: In Render Dashboard
1. Go to your Web Service
2. Click "Environment" tab
3. Click "Add Environment Variable"
4. Add each variable one by one

### Step 2: Format Examples

**Single Value:**
```
DJANGO_DEBUG = False
```

**Multiple Values (comma-separated):**
```
DJANGO_ALLOWED_HOSTS = pie-global-funitures.onrender.com,www.mysite.com
```

```
CORS_ALLOWED_ORIGINS = https://pie-global-funitures.vercel.app,https://www.mysite.com
```

**Note:** Vercel preview deployments (e.g., `*-palmerscott254-gifs-projects.vercel.app`) are automatically allowed via regex pattern. You only need to add your production Vercel domain.

---

## Important Notes

⚠️ **Never commit `.env` file to GitHub** - Keep secrets secret!

⚠️ **DATABASE_URL** - Render sets this automatically when you link your PostgreSQL database

⚠️ **ALLOWED_HOSTS** - Don't include `https://` or `http://`, just the domain

✅ **After adding variables** - Click "Manual Deploy" or push to trigger rebuild

---

## Gmail App Password Setup

If using Gmail for email:

1. Go to https://myaccount.google.com/security
2. Enable 2-Factor Authentication (required)
3. Go to "App passwords" section
4. Generate new app password for "Mail"
5. Use this password (not your regular Gmail password)

---

## Verification Checklist

After deployment, verify:

✅ Health check works: `https://your-app.onrender.com/api/health/`
✅ Admin panel loads: `https://your-app.onrender.com/admin/`
✅ API endpoints work: `https://your-app.onrender.com/api/products/`
✅ CORS allows frontend: Check browser console for CORS errors
✅ Database connected: Try creating data in admin panel
✅ Static files load: Admin CSS should work

---

## Quick Commands

```bash
# In Render Shell:

# Create superuser
python manage.py createsuperuser

# Check configuration
python manage.py check --deploy

# Run migrations
python manage.py migrate

# Test database
python manage.py dbshell
```
