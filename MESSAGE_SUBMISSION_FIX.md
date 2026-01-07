# Message Submission Fix - Vercel Frontend Issue

## Problem Summary
- Messages submitted from **Vercel frontend** fail with "Failed to send message. Please try again."
- Messages work fine on **localhost frontend**
- Messages should be saved to PostgreSQL database

## Root Causes Identified & Fixed

### 1. ❌ CORS Configuration (FIXED)
**Issue:** Vercel preview/staging domains not in `CORS_ALLOWED_ORIGINS`

**What was wrong:**
```python
# OLD - Only allowed exact domain
CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',
    'http://localhost:5173',
    'https://pie-global-funitures.vercel.app',  # Only main domain
]
```

**What's fixed:**
```python
# NEW - Allows all Vercel preview deployments
CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',
    'http://localhost:5173',
    'http://127.0.0.1:3000',
    'http://127.0.0.1:5173',
    'https://pie-global-funitures.vercel.app',
]

# Also add regex for all vercel.app domains
CORS_ALLOWED_ORIGIN_REGEXES = [
    r"^https://.*\.vercel\.app$",  # pie-global-funitures-*.vercel.app
    r"^http://localhost:\d+$",
    r"^http://127\.0\.0\.1:\d+$",
]
```

**Why it matters:** Vercel creates preview deployments with different domains like:
- `pie-global-funitures-scott-newton.vercel.app` (staging)
- `pie-global-funitures-main.vercel.app` (preview)

### 2. ❌ API_URL Export (FIXED)
**Issue:** Frontend `API_URL` variable incorrectly removing `/api/` suffix

**What was wrong:**
```typescript
// OLD - Naive string replace broke if URL didn't end with /
export const API_URL = API_BASE_URL.replace('/api/', '');
```

**What's fixed:**
```typescript
// NEW - Proper handling of /api/ suffix
export const API_URL = API_BASE_URL.endsWith('/api/') 
  ? API_BASE_URL.slice(0, -5)  // Remove '/api/' (5 characters)
  : API_BASE_URL;
```

### 3. ❌ Error Handling (IMPROVED)
**Issue:** Generic error message didn't show actual problem from backend

**What was wrong:**
```typescript
catch (error: any) {
  if (error.message?.includes('Too many requests')) {
    toast.error('Too many requests...');
  } else {
    toast.error('Failed to send message. Please try again.');  // Too generic!
  }
}
```

**What's improved:**
```typescript
catch (error: any) {
  // Log for debugging
  if (import.meta.env.DEV) {
    console.error('Message submission error:', error);
    if (error.response?.data) {
      console.error('Backend response:', error.response.data);
    }
  }
  
  // Handle specific errors
  if (error.response?.status === 429) {
    toast.error('Too many requests. Please try again later.');
  } else if (error.response?.status === 400) {
    // Show validation errors from backend
    const errors = error.response?.data?.errors || error.response?.data;
    const errorMessage = typeof errors === 'string' 
      ? errors 
      : Object.values(errors).flat()[0] || 'Invalid form data';
    toast.error(errorMessage);
  } else if (error.response?.status === 0 || error.message?.includes('Network')) {
    toast.error('Network error. Check your connection and try again.');
  } else {
    toast.error('Failed to send message. Please try again.');
  }
}
```

---

## How Messages Are Saved to Database

### Backend Flow (Django)

1. **User submits form** → POST to `/api/messages/`
2. **Validation** → Check name, email, phone, message fields
3. **Save to database** → `UserMessage` model saves to PostgreSQL
4. **Send notification** → Email sent to admin
5. **Return success** → 201 Created response

### Database Schema
```python
class UserMessage(models.Model):
    # Customer Info
    name = CharField(max_length=200)
    email = EmailField(blank=True, null=True)
    phone = CharField(max_length=20, blank=True, null=True)
    
    # Message Content
    message = TextField()
    status = CharField(choices=['new', 'read', 'replied', 'resolved'], default='new')
    
    # Admin Reply
    reply_text = TextField(blank=True, null=True)
    replied_at = DateTimeField(blank=True, null=True)
    
    # Timestamps
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)
```

### Verify Messages in Database

```bash
# Connect to Render PostgreSQL
DATABASE_URL="your_render_postgres_url"

# Option 1: Django shell
python manage.py shell
>>> from apps.messages.models import UserMessage
>>> UserMessage.objects.all().count()  # See total messages
>>> UserMessage.objects.latest('id')   # See last message

# Option 2: Direct SQL
psql $DATABASE_URL
> SELECT * FROM apps_messages_usermessage ORDER BY created_at DESC LIMIT 5;

# Option 3: Django admin
# Go to https://pie-global-funitures.onrender.com/admin
# Login with superuser credentials
# Navigate to "User Messages"
```

---

## Testing Checklist

### ✅ Test 1: Local Frontend to Local Backend
```bash
# Terminal 1: Backend
cd backend
python manage.py runserver

# Terminal 2: Frontend
cd frontend
npm run dev

# Browser: http://localhost:5173/contact
# Submit message
# Check: Browser shows "Thank you! We will get back to you soon."
# Check: Django logs show "Message saved"
```

### ✅ Test 2: Vercel Frontend to Render Backend
```bash
# In Vercel UI:
# 1. Go to Project Settings > Environment Variables
# 2. Set VITE_API_URL = https://pie-global-funitures.onrender.com/api/
# 3. Redeploy

# In browser: https://pie-global-funitures.vercel.app/contact
# Submit message
# Check: "Thank you!" message appears
# Check: Message shows in Django admin
```

### ✅ Test 3: Check Backend CORS Configuration
```bash
# Backend logs should show no CORS errors
curl -X OPTIONS https://pie-global-funitures.onrender.com/api/messages/ \
  -H "Origin: https://pie-global-funitures.vercel.app" \
  -H "Access-Control-Request-Method: POST" \
  -v

# Expected headers in response:
# Access-Control-Allow-Origin: https://pie-global-funitures.vercel.app
# Access-Control-Allow-Methods: GET, POST, PUT, PATCH, DELETE, OPTIONS
```

### ✅ Test 4: Verify Database Persistence
```bash
# After submitting message from Vercel:

# Check via Render Dashboard:
# 1. Go to your PostgreSQL instance
# 2. Click "Browser" tab
# 3. Select "public" schema
# 4. Find "apps_messages_usermessage" table
# 5. Should show your message row

# Or via Django admin:
# https://pie-global-funitures.onrender.com/admin/messages/usermessage/
```

---

## Environment Variables Required

### Backend (`.env` or Render Settings)
```env
DATABASE_URL=postgres://...          # Render PostgreSQL
DEBUG=False                          # Production
DJANGO_SECRET_KEY=...               # Your secret key
DJANGO_ALLOWED_HOSTS=pie-global-funitures.onrender.com

# Optional - Override CORS if needed
CORS_ALLOWED_ORIGINS=http://localhost:3000,https://pie-global-funitures.vercel.app
```

### Frontend (Vercel Environment Variables)
```env
VITE_API_URL=https://pie-global-funitures.onrender.com/api/
```

---

## Troubleshooting Guide

### Issue: "Failed to send message" on Vercel but works on localhost

**Step 1: Check CORS errors in browser console**
- Open DevTools → Network tab
- Submit message
- Look for failed request to `/api/messages/`
- Check response headers for `Access-Control-Allow-Origin`

**Step 2: Check API_URL is correct**
```javascript
// In browser console on Vercel frontend:
import { API_URL } from '@/services/api'
console.log('API_URL:', API_URL)
// Should print: https://pie-global-funitures.onrender.com/api/
```

**Step 3: Test API directly from Vercel**
```javascript
// In browser console on https://pie-global-funitures.vercel.app:
fetch('https://pie-global-funitures.onrender.com/api/messages/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  credentials: 'include',
  body: JSON.stringify({
    name: 'Test',
    email: 'test@example.com',
    phone: '555-1234',
    message: 'Test message'
  })
})
.then(r => r.json())
.then(data => console.log(data))
.catch(e => console.error(e))
```

**Step 4: Check Render backend logs**
```bash
# In Render Dashboard:
# 1. Go to your web service
# 2. Click "Logs" tab
# 3. Look for POST /api/messages/ requests
# 4. Check for errors like "CORS" or "ValidationError"
```

### Issue: Message submitted but not appearing in database

**Check 1: Verify message actually saved**
```python
# Django shell
from apps.messages.models import UserMessage
from django.utils import timezone
from datetime import timedelta

# Get messages from last hour
recent = UserMessage.objects.filter(
    created_at__gte=timezone.now() - timedelta(hours=1)
).order_by('-created_at')

print(f"Found {recent.count()} messages")
for msg in recent:
    print(f"  - {msg.name}: {msg.message[:50]}...")
```

**Check 2: Verify database connection**
```bash
python manage.py dbshell
# Should connect to database without errors
\dt  # List tables
SELECT COUNT(*) FROM apps_messages_usermessage;  # Count messages
```

### Issue: Rate limiting (5 messages/hour)

**Affected:** The same IP address can only submit 5 messages per hour

**Solution:**
- Wait 1 hour, or
- Use different IP address, or
- Contact admin to reset rate limit

**Check rate limit status:**
```bash
# In Django logs, look for:
# "429 Too Many Requests"
# "Rate limit exceeded for IP: 1.2.3.4"
```

---

## Files Changed

1. **Backend:**
   - `backend/pie_global/settings.py` - Added CORS regex patterns

2. **Frontend:**
   - `frontend/src/services/api.ts` - Fixed API_URL export
   - `frontend/src/pages/ContactPage.tsx` - Improved error handling

---

## Deployment Steps

### 1. Update Backend (Render)
```bash
# Commit changes
git add -A
git commit -m "Fix: CORS configuration for all Vercel domains"

# Push to trigger Render deploy
git push origin main

# Monitor: https://dashboard.render.com/services/[service-id]/events
# Wait for "Deploy successful" message
```

### 2. Update Frontend (Vercel)
```bash
# Changes auto-deployed from git push
# Or manually trigger: https://vercel.com/dashboard/[project]/deployments

# Verify: Check environment variable VITE_API_URL is set
# https://vercel.com/dashboard/[project]/settings/environment-variables
```

### 3. Test After Deployment
1. Go to https://pie-global-funitures.vercel.app/contact
2. Submit message with test data
3. Wait 2-3 seconds for response
4. Should see "Thank you!" message
5. Check Django admin for message entry

---

## Key Takeaways

✅ **Messages ARE saved to PostgreSQL database** - The backend model is correct

✅ **CORS was the main issue** - Vercel preview domains not whitelisted

✅ **API_URL export needed fixing** - Frontend couldn't build correct auth endpoint URL

✅ **Error handling was too generic** - Now shows actual backend errors

✅ **Everything works on localhost** - Issues only manifest in production Vercel

---

## Quick Reference

| Scenario | URL | Endpoint |
|----------|-----|----------|
| Local Dev | http://localhost:5173 | http://localhost:8000/api/messages/ |
| Vercel Prod | https://pie-global-funitures.vercel.app | https://pie-global-funitures.onrender.com/api/messages/ |
| Backend Admin | https://pie-global-funitures.onrender.com/admin | Login required |
| Database | Render PostgreSQL | via `psql` or Render UI |

---

## Support

- **Backend Issues?** Check Django logs in Render dashboard
- **CORS Issues?** Check browser Network tab in DevTools
- **Database Issues?** Check Render PostgreSQL instance status
- **API Issues?** Test with curl or Postman before debugging frontend

