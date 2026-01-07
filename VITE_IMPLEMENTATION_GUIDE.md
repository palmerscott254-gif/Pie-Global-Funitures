# Vite VITE_API_URL Fix - Implementation Guide

**Status:** ✅ Code fixes applied  
**Files Modified:** 3 (vite.config.ts, api.ts, .env files)  
**Time to Deploy:** ~10 minutes

---

## What Was Fixed

### Issue 1: Environment Variable Not Exposed in Build
**Before:** vite.config.ts had no `define` option  
**After:** Added explicit environment variable definition

### Issue 2: Unsafe Fallback Logic
**Before:** Checked `window.location.hostname === 'localhost'` (too broad)  
**After:** Created `getApiUrl()` function with 3-tier priority system

### Issue 3: Silent Failures
**Before:** No logging in dev mode  
**After:** Added debug logging to help troubleshoot

### Issue 4: Missing Environment Marker
**Before:** No way to distinguish dev vs prod  
**After:** Added `VITE_ENV` variable for environment detection

---

## Code Changes Summary

### 1. frontend/vite.config.ts
```diff
+ // Add this inside defineConfig():
+ define: {
+   'import.meta.env.VITE_API_URL': JSON.stringify(
+     process.env.VITE_API_URL || 'http://localhost:8000/api/'
+   ),
+ },
```

**Why:** Ensures Vite properly exposes VITE_API_URL from environment during build.

---

### 2. frontend/src/services/api.ts

**Replaced inline API URL logic with:**
```typescript
const getApiUrl = (): string => {
  // Priority 1: Build-time env var (from Vercel or .env)
  const envUrl = import.meta.env.VITE_API_URL;
  if (envUrl && typeof envUrl === 'string' && envUrl.trim()) {
    return envUrl;
  }

  // Priority 2: Local development detection
  if (typeof window !== 'undefined') {
    const isLocal =
      window.location.hostname === 'localhost' ||
      window.location.hostname === '127.0.0.1' ||
      window.location.hostname.startsWith('192.168.') ||
      window.location.hostname.startsWith('10.');
    if (isLocal) return 'http://localhost:8000/api/';
  }

  // Priority 3: Production fallback
  return 'https://pie-global-funitures.onrender.com/api/';
};

const API_BASE_URL = getApiUrl();

// Added debug logging
if (import.meta.env.DEV) {
  console.debug(
    '[API Configuration] Using API URL:',
    API_BASE_URL,
    'from env:',
    import.meta.env.VITE_API_URL || '(not set, using fallback)'
  );
}
```

**Why:** 
- Explicit priority system (no ambiguity)
- Better local IP detection
- Debug logging for troubleshooting

---

### 3. frontend/.env
```diff
  VITE_API_URL=http://localhost:8000/api/
+ VITE_ENV=development
```

**Why:** Explicit env marker helps with debugging.

---

### 4. frontend/.env.production
```diff
  VITE_API_URL=https://pie-global-funitures.onrender.com/api/
+ VITE_ENV=production
```

**Why:** Clear documentation that this is for production builds.

---

## Deployment Steps

### Step 1: Verify Local Changes

```bash
cd frontend

# Check files were modified
git status

# Should show:
# - vite.config.ts (modified)
# - src/services/api.ts (modified)
# - .env (modified)
# - .env.production (modified)
```

### Step 2: Test Locally

```bash
# Start dev server
npm run dev

# Open browser console (F12 > Console)
# Should see:
# [API Configuration] Using API URL: http://localhost:8000/api/ from env: (not set, using fallback)

# This is expected in dev - it shows the fallback logic working
```

### Step 3: Build Locally

```bash
# Build production bundle
npm run build

# Check dist/index.html contains your backend URL
grep -i "onrender.com" dist/index.html

# Should find your Render domain hardcoded in JS
```

### Step 4: Set Vercel Environment Variables

**CRITICAL - Do this BEFORE deploying:**

1. Go to Vercel Dashboard
2. Select your project
3. Project Settings > Environment Variables
4. Click "Add"
   - **Name:** `VITE_API_URL`
   - **Value:** `https://pie-global-funitures.onrender.com/api/`
   - **Scope:** Production
5. Click "Save"

**Verify:**
- Variable shows in list
- Marked for "Production"

### Step 5: Deploy

```bash
# Commit changes
git add frontend/vite.config.ts frontend/src/services/api.ts frontend/.env*
git commit -m "Fix: Improve VITE_API_URL configuration with explicit env var handling"

# Push to GitHub
git push origin main

# Vercel auto-deploys on push
```

### Step 6: Monitor Vercel Build

1. Go to Vercel Dashboard
2. Deployments tab
3. Watch for your new deployment
4. Check build logs for any errors

**Look for:**
- ✅ Build successful
- ✅ No VITE_API_URL warnings
- ✅ Deployment complete

### Step 7: Test Production

```bash
# Visit your Vercel site
# Open DevTools > Console (F12)
# Make sure no errors about API URL

# Open Network tab
# Trigger an API call (load products page, etc.)
# Verify request goes to: https://pie-global-funitures.onrender.com/api/products/

# Should see: 200 OK (not 404 or CORS error)
```

---

## Verification Checklist

- [ ] Local dev works: `npm run dev` runs without API errors
- [ ] Build succeeds: `npm run build` completes successfully
- [ ] Debug logging appears: Check browser console for `[API Configuration]` message
- [ ] Vercel env var set: Check Project Settings > Environment Variables
- [ ] Production build shows correct URL: `grep onrender dist/index.html`
- [ ] Production site loads: Visit Vercel deployment, no 404 errors
- [ ] Network shows correct endpoint: DevTools Network tab shows Render backend URL

---

## Testing the Fix

### Local Development Test
```bash
# Terminal 1: Start backend
cd backend && python manage.py runserver

# Terminal 2: Start frontend
cd frontend && npm run dev

# Browser: http://localhost:3000
# Console: Should see [API Configuration] log
# Products load: Should work without errors
```

### Production Test
```bash
# Visit: https://pie-global-funitures.vercel.app

# Open DevTools F12 > Console
# No errors about API configuration

# Open Network tab
# Load products page
# Check request URL in Network tab
# Should be: https://pie-global-funitures.onrender.com/api/products/
# Status: 200 OK

# Products display on page: ✅ Success
```

---

## Troubleshooting

### Problem: Still Getting Undefined
**Check:**
1. Is Vercel env var `VITE_API_URL` set in Project Settings?
2. Did Vercel redeploy after adding the env var?
3. Did you clear browser cache? (Ctrl+Shift+Delete)

**Fix:**
```bash
# Force Vercel rebuild
vercel deploy --prod --clear
```

---

### Problem: API requests to wrong URL
**Check:**
1. What URL shows in Network tab?
2. Open browser console, search for `[API Configuration]` message
3. What does it show as the API URL?

**Fix:**
1. Check Vercel env var is correctly set
2. Verify .env.production has correct URL
3. Check vite.config.ts has the `define` option

---

### Problem: Local dev broken
**Check:**
1. Backend running? `python manage.py runserver`
2. Did you run `npm run dev`?
3. Check browser console for errors

**Fix:**
```bash
# Reinstall dependencies (if needed)
npm install

# Clear build cache
rm -rf node_modules dist
npm install
npm run dev
```

---

## How It Works Now

### Priority System
```
1. VITE_API_URL from Vercel env vars
   ↓
2. VITE_API_URL from .env.production/.env
   ↓
3. vite.config.ts define fallback
   ↓
4. Runtime detection (localhost vs production)
   ↓
5. Hardcoded fallback (Render backend)
```

### Development Flow
```
npm run dev
  ↓
Reads .env
  ↓
VITE_API_URL = http://localhost:8000/api/
  ↓
Browser console shows: [API Configuration] Using API URL: http://localhost:8000/api/
  ↓
API calls work correctly
```

### Production Flow (Vercel)
```
vercel deploy (or git push)
  ↓
Reads VITE_API_URL from Vercel env vars
  ↓
Reads from fallback: .env.production
  ↓
vite build with VITE_API_URL set
  ↓
Hardcodes Render URL into dist/index.html
  ↓
No debug logging in production
  ↓
API calls go to correct backend
```

---

## Summary

| Item | Before | After |
|------|--------|-------|
| **Build time exposure** | Not explicit | Explicit in vite.config.ts |
| **Fallback logic** | Checks hostname only | 3-tier priority system |
| **Debug info** | None | Console logging in dev |
| **Local IP detection** | localhost only | localhost, 127.0.0.1, 192.168.*, 10.* |
| **Error messages** | Generic | Specific with env var hint |
| **Documentation** | Minimal | Detailed comments |

---

## Next Steps

1. ✅ Code changes applied (done)
2. **Set Vercel env var** (do this)
3. **Deploy** (do this)
4. **Verify** (do this)
5. **Test on production** (do this)

---

**Status:** Ready for Deployment  
**Estimated Time:** 10 minutes  
**Risk:** Low (no breaking changes)
