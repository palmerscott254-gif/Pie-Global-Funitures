# CORS Issue Fix - Immediate Action Required

## Problem
Your Vercel frontend cannot fetch images/videos from Render backend due to CORS (Cross-Origin Resource Sharing) blocking.

## Solution Applied
The Django settings have been updated to support Vercel deployments automatically:
- ✅ Added Vercel production domain to defaults
- ✅ Added regex pattern to allow ALL Vercel preview deployments (`*.vercel.app`)
- ✅ Fixed CORS_ALLOW_ALL_ORIGINS default to False for security

## Required Steps on Render

### Option 1: Update Environment Variable (Recommended)
1. Go to https://dashboard.render.com
2. Select your backend service: `pie-global-funitures`
3. Click **Environment** tab
4. Find or add `CORS_ALLOWED_ORIGINS` variable
5. Set value to:
   ```
   https://pie-global-funitures.vercel.app
   ```
   (No need to add preview URLs - they're auto-allowed via regex)

6. Click **Save Changes**
7. Render will automatically redeploy

### Option 2: Manual Redeploy
If you've already pushed these code changes to GitHub:
1. Go to your Render dashboard
2. Click **Manual Deploy** → **Deploy latest commit**
3. Wait for deployment to complete (~2-3 minutes)

## Verification

After deployment, check:
1. Open browser DevTools (F12) on your Vercel site
2. Go to Console tab
3. Refresh the page
4. You should see:
   - ✅ Status 200 for `/api/sliders/` requests
   - ✅ Images and videos loading
   - ❌ NO "CORS policy" errors

## Testing Locally

To test the changes locally:

```powershell
cd backend
python manage.py runserver
```

Then visit your frontend and check if it connects properly.

## What Changed

### In `settings.py`:
- Updated default CORS origins to include Vercel
- Added `CORS_ALLOWED_ORIGIN_REGEXES` for Vercel preview URLs
- Changed `CORS_ALLOW_ALL_ORIGINS` default from `DEBUG` to `False`

### Why This Works:
- Production domain explicitly allowed
- Preview deployments (palmerscott254-gifs-projects.vercel.app) automatically allowed
- Secure: doesn't allow ALL origins, only Vercel domains

## Troubleshooting

### Still seeing CORS errors?
1. Check Render logs: Dashboard → Logs
2. Verify environment variable is set correctly
3. Try clearing browser cache (Ctrl+Shift+Delete)
4. Check Network tab in DevTools for actual request/response

### Need to allow other domains?
Add them comma-separated:
```
CORS_ALLOWED_ORIGINS=https://pie-global-funitures.vercel.app,https://custom-domain.com
```

## Security Note

✅ **Safe for production** - Only allows:
- Your localhost (dev)
- Your Vercel domains
- NOT allowing wildcard (*) origins

---

**Status:** Ready to deploy - Push to GitHub and Render will auto-deploy, or manually deploy from dashboard.
