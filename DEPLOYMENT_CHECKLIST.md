# Production Deployment Checklist: Django + Vercel CORS Fix

**Status:** Critical issues fixed. Use this checklist to verify in production.

---

## 📋 Pre-Deployment Verification (Local)

### Backend (Django on Render)

- [ ] **ALLOWED_HOSTS is explicit** (no wildcards)
  ```bash
  # Check settings.py
  grep "pie-global-funitures.onrender.com" backend/pie_global/settings.py
  ```
  Expected: Your Render domain is listed explicitly

- [ ] **APPEND_SLASH is set**
  ```bash
  grep "APPEND_SLASH = True" backend/pie_global/settings.py
  ```
  Expected: Appears in settings

- [ ] **CORS_ALLOW_ALL_ORIGINS is False**
  ```bash
  grep "CORS_ALLOW_ALL_ORIGINS = False" backend/pie_global/settings.py
  ```
  Expected: Not tied to DEBUG anymore

- [ ] **CORS_ALLOWED_ORIGINS includes Vercel domain**
  ```bash
  grep "pie-global-funitures.vercel.app" backend/pie_global/settings.py
  ```
  Expected: `https://pie-global-funitures.vercel.app` is in the list

- [ ] **Django middleware order is correct**
  ```bash
  grep -A 8 "MIDDLEWARE = " backend/pie_global/settings.py
  ```
  Expected: `corsheaders.middleware.CorsMiddleware` is FIRST

- [ ] **Requirements include django-cors-headers**
  ```bash
  grep "django-cors-headers" backend/requirements.txt
  ```
  Expected: `django-cors-headers==4.6.0` (or newer)

### Frontend (Vercel)

- [ ] **API URLs have trailing slashes**
  ```bash
  grep -n "'/products/'" frontend/src/services/api.ts
  ```
  Expected: All API endpoint calls use trailing slashes

- [ ] **withCredentials is true**
  ```bash
  grep "withCredentials: true" frontend/src/services/api.ts
  ```
  Expected: Set to `true` for session/auth handling

- [ ] **vercel.json doesn't proxy /api/**
  ```bash
  cat frontend/vercel.json
  ```
  Expected: No `/api/:path*` rewrite rule; only SPA fallback to `/index.html`

- [ ] **Environment variable uses trailing slash**
  ```bash
  grep "VITE_API_URL=" frontend/.env.production
  ```
  Expected: `https://pie-global-funitures.onrender.com/api/` (with `/`)

- [ ] **No hardcoded localhost URLs in production build**
  ```bash
  grep -r "localhost" frontend/src --exclude-dir=node_modules
  ```
  Expected: Only in `.env.example` or local dev comments

---

## 🚀 Render Backend Deployment Steps

### 1. Set Environment Variables on Render

Go to **Render Dashboard** > Your Service > **Environment**

Required variables (if not auto-set):
```
DJANGO_DEBUG=False
DJANGO_SECRET_KEY=<use-strong-random-key>
DJANGO_ALLOWED_HOSTS=pie-global-funitures.onrender.com
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173,https://pie-global-funitures.vercel.app
CSRF_TRUSTED_ORIGINS=http://localhost:3000,http://localhost:5173,https://pie-global-funitures.vercel.app,https://pie-global-funitures.onrender.com
```

**Note:** Render auto-sets `RENDER_EXTERNAL_URL`. Verify in Render logs:
```
INFO: RENDER_EXTERNAL_URL=https://pie-global-funitures.onrender.com
```

### 2. Deploy Backend

```bash
# Push code to Render (if using git integration)
git push origin main

# Or trigger manual deploy in Render dashboard
```

### 3. Verify Backend Startup

Check Render logs for:
```
✓ ALLOWED_HOSTS includes: ['pie-global-funitures.onrender.com', ...]
✓ DEBUG = False
✓ CORS middleware loaded
✓ Database connected successfully
```

---

## 🌐 Vercel Frontend Deployment Steps

### 1. Set Environment Variables on Vercel

Go to **Vercel Dashboard** > Project Settings > **Environment Variables**

Add:
```
VITE_API_URL=https://pie-global-funitures.onrender.com/api/
```

- Scope: **Production** (and **Preview** if you want)
- Do NOT use rewrites proxy

### 2. Deploy Frontend

```bash
# Option A: Git integration (auto-deploy on push)
git push origin main

# Option B: Manual deployment
vercel deploy --prod
```

### 3. Verify Vercel Build

Check build logs for:
```
✓ VITE_API_URL loaded from environment
✓ Build successful, no hardcoded localhost URLs
```

---

## 🧪 Production Testing (Post-Deployment)

### Test 1: CORS Preflight Check

```bash
# From your production Vercel domain, test OPTIONS request
curl -X OPTIONS https://pie-global-funitures.onrender.com/api/products/ \
  -H "Origin: https://pie-global-funitures.vercel.app" \
  -H "Access-Control-Request-Method: GET" \
  -v

# Expected response headers:
# Access-Control-Allow-Origin: https://pie-global-funitures.vercel.app
# Access-Control-Allow-Methods: GET, HEAD, OPTIONS, POST, PUT, PATCH, DELETE
# Access-Control-Allow-Credentials: true
```

### Test 2: Actual GET Request

```bash
curl -X GET https://pie-global-funitures.onrender.com/api/products/ \
  -H "Origin: https://pie-global-funitures.vercel.app" \
  -H "Content-Type: application/json" \
  -v

# Expected: 200 OK with CORS headers + data
```

### Test 3: Frontend API Call in Browser

1. Open **Vercel production site** in browser
2. Open **DevTools** > **Network** tab
3. Trigger a data fetch (e.g., load products page)
4. Check the API request:
   - ✓ **Status:** 200 (not 403, 401, or error)
   - ✓ **Response Headers:** `access-control-allow-origin: https://pie-global-funitures.vercel.app`
   - ✓ **Response Body:** JSON data (not empty or error)

### Test 4: Check for Silent Failures in Browser Console

Open Vercel site in browser, check **Console** for:
- ❌ NO `CORS policy: Cross-Origin Request Blocked` errors
- ❌ NO `Failed to fetch` errors
- ❌ NO `401 Unauthorized` errors
- ✓ Only normal console logs (if any)

### Test 5: Verify ALLOWED_HOSTS Rejection

Try accessing backend with wrong Host header:
```bash
curl -X GET https://pie-global-funitures.onrender.com/api/products/ \
  -H "Host: wrong-domain.com" \
  -v

# Expected: 400 Bad Request (Django rejects bad Host)
# This is GOOD - shows ALLOWED_HOSTS protection is active
```

---

## 🔍 Common Failure Patterns & Fixes

| Error | Root Cause | Fix |
|-------|-----------|-----|
| `CORS policy: Cross-Origin Request Blocked` | `CORS_ALLOWED_ORIGINS` doesn't include frontend domain | Update `CORS_ALLOWED_ORIGINS` env var on Render |
| `Blocked by CORS policy: No 'Access-Control-Allow-Credentials' header` | Frontend sends `withCredentials: true` but backend not configured | Ensure `CORS_ALLOW_CREDENTIALS = True` in settings |
| `400 Bad Request` | ALLOWED_HOSTS doesn't match request Host header | Check Render env var `DJANGO_ALLOWED_HOSTS` |
| `Vercel pages work, API returns 404` | Missing trailing slash in Django URLs | Ensure endpoints use `/` (e.g., `/products/`, not `/products`) |
| `Network timeout when calling API` | Render instance is sleeping (free tier) | Upgrade to paid plan or use cold start timeout config |
| `401 Unauthorized (CSRF)` | CSRF token missing or origin not in CSRF_TRUSTED_ORIGINS | Check `CSRF_TRUSTED_ORIGINS` includes frontend domain |

---

## 🔐 Security Checklist

- [ ] **DEBUG = False** in production (Render env: `DJANGO_DEBUG=False`)
- [ ] **ALLOWED_HOSTS** contains ONLY your Render domain (no wildcards, no `.onrender.com`)
- [ ] **SECRET_KEY** is strong and unique (not the default)
- [ ] **CORS_ALLOW_ALL_ORIGINS = False** (never allow all origins in production)
- [ ] **withCredentials: true** only if using session/auth
- [ ] **HTTPS only** - both Vercel and Render use HTTPS
- [ ] **No hardcoded credentials** in code or .env files (use env vars)
- [ ] **SECURE_SSL_REDIRECT = True** in production settings
- [ ] **HSTS headers enabled** (1 year expiry)
- [ ] **X-Frame-Options: DENY** to prevent clickjacking

---

## 📊 Monitoring Post-Deployment

### Backend (Render) Logs

```bash
# Check Render logs for CORS errors
# Render Dashboard > Service > Logs
# Search for: "CORS", "ALLOWED_HOSTS", "400 Bad Request"
```

### Frontend (Vercel) Logs

```bash
# Check Vercel logs for failed API calls
# Vercel Dashboard > Project > Deployments > Logs
# Search for: "VITE_API_URL", "fetch failed", "CORS"
```

### Real User Monitoring

Add this to your `frontend/src/services/api.ts` response interceptor:

```typescript
(error: AxiosError) => {
  // Production monitoring
  if (!import.meta.env.DEV && error.response?.status === 403) {
    console.error('CORS Rejected:', {
      origin: window.location.origin,
      targetUrl: error.config?.url,
      timestamp: new Date().toISOString(),
    });
    // Send to logging service (Sentry, LogRocket, etc.)
  }
  return Promise.reject(error);
}
```

---

## ✅ Final Verification Checklist

After all deployments, verify:

- [ ] Products page loads without CORS errors
- [ ] API calls return 200 status in Network tab
- [ ] `access-control-allow-origin` header visible in responses
- [ ] No 400/401/403 errors before reaching views
- [ ] Database queries work (data displays correctly)
- [ ] Static files load (CSS, images, etc.)
- [ ] Forms submit without CSRF errors (if applicable)
- [ ] Slow API calls don't timeout (15s timeout is set)

---

## 🚨 Emergency Troubleshooting

If things still don't work after all fixes:

### Step 1: Confirm Environment Variables on Render

```bash
# SSH into Render and check what's actually set
# Render Dashboard > Service > Console
echo $DJANGO_ALLOWED_HOSTS
echo $CORS_ALLOWED_ORIGINS
echo $DJANGO_DEBUG
echo $RENDER_EXTERNAL_URL
```

### Step 2: Test Directly from CLI

```bash
# Replace YOUR_RENDER_DOMAIN with actual domain
curl -X GET https://pie-global-funitures.onrender.com/api/products/ \
  -H "Origin: https://pie-global-funitures.vercel.app" \
  -H "User-Agent: curl-test" \
  -v 2>&1 | grep -i "access-control\|status\|content-type"
```

### Step 3: Check Render Logs for Errors

Look for:
- `DisallowedHost` errors → ALLOWED_HOSTS issue
- `No 'Access-Control-Allow-Origin'` → CORS configuration issue
- `ModuleNotFoundError` → Missing dependency
- `OperationalError` → Database connection issue

### Step 4: Verify Vercel Environment Variable

```bash
# On Vercel, the build log should show:
# Loaded VITE_API_URL=https://pie-global-funitures.onrender.com/api/
```

---

## 📞 Support & References

- **Django CORS Headers Docs:** https://github.com/adamchainz/django-cors-headers#setup
- **Render Docs:** https://render.com/docs
- **Vercel Environment Variables:** https://vercel.com/docs/concepts/projects/environment-variables
- **MDN CORS Guide:** https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS

---

**Last Updated:** January 7, 2026
**Status:** Ready for Production Deployment
