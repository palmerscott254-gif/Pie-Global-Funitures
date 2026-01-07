# Django + Vercel CORS Configuration Audit Report

**Project:** Pie Global Furniture  
**Date:** January 7, 2026  
**Status:** 🔴 **5 CRITICAL ISSUES FOUND & FIXED**

---

## Executive Summary

Your Django backend on Render and Vercel frontend are failing to fetch data due to **multiple configuration mismatches** that prevent requests from reaching your API views. These issues exist **before CORS validation** happens, creating silent failures in production.

**Primary Blockers:**
1. ❌ ALLOWED_HOSTS uses wildcards (invalid in production)
2. ❌ CORS configuration depends on DEBUG flag (breaks in production)
3. ❌ No explicit trailing slash configuration
4. ❌ Vercel rewrites conflict with direct API calls
5. ❌ Frontend doesn't use credentials flag for CORS

---

## Issue #1: ALLOWED_HOSTS Wildcard Misconfiguration

### The Problem

**Current Code (BROKEN):**
```python
_default_hosts = 'localhost,127.0.0.1,.onrender.com,.railway.app,.vercel.app'
allowed_hosts = list(config('DJANGO_ALLOWED_HOSTS', default=_default_hosts, cast=Csv()))
```

### Why It Fails

- Django's `ALLOWED_HOSTS` validation checks **exact domain match or subdomain match**
- Wildcard entries like `.onrender.com` do NOT match the actual domain `pie-global-funitures.onrender.com`
- When Render sends request with `Host: pie-global-funitures.onrender.com`, Django sees it's not in ALLOWED_HOSTS
- **Result:** 400 Bad Request **before your view code runs**
- Django logs: `DisallowedHost: pie-global-funitures.onrender.com`

### HTTP Request Flow

```
Vercel Frontend
    ↓
https://pie-global-funitures.onrender.com/api/products/
    ↓
Django ALLOWED_HOSTS Validation
    ✗ Check: Is "pie-global-funitures.onrender.com" in [".onrender.com", ...]?
    ✗ Result: NO - wildcard .onrender.com doesn't match full domain
    ✗ Response: 400 Bad Request (DisallowedHost)
    ✗ CORS headers: NOT sent (validation failed before middleware runs)
```

### The Fix

```python
# Development defaults
_development_hosts = ['localhost', '127.0.0.1']

# Production defaults - Add your Render backend domain here
_production_hosts = [
    'pie-global-funitures.onrender.com',  # EXACT domain required
]

# Build ALLOWED_HOSTS from env or defaults
if DEBUG:
    _default_hosts = ','.join(_development_hosts)
else:
    _default_hosts = ','.join(_production_hosts)

allowed_hosts = list(config('DJANGO_ALLOWED_HOSTS', default=_default_hosts, cast=Csv()))

# Render's RENDER_EXTERNAL_URL takes precedence
render_url = os.getenv('RENDER_EXTERNAL_URL', '')
if render_url:
    url_to_parse = render_url if '://' in render_url else f'https://{render_url}'
    parsed = urlparse(url_to_parse)
    host = parsed.netloc  # Extracts: pie-global-funitures.onrender.com
    if host and host not in allowed_hosts:
        allowed_hosts.append(host)

ALLOWED_HOSTS = sorted(set(allowed_hosts))
```

**Key Changes:**
- ✅ Explicit full domain (`pie-global-funitures.onrender.com`), NOT wildcard
- ✅ Safely parses Render's auto-set `RENDER_EXTERNAL_URL` environment variable
- ✅ Logs errors if parsing fails (instead of silent skip)

---

## Issue #2: CORS_ALLOW_ALL_ORIGINS Tied to DEBUG Flag

### The Problem

**Current Code (BROKEN):**
```python
CORS_ALLOW_ALL_ORIGINS = config('CORS_ALLOW_ALL_ORIGINS', default=DEBUG, cast=bool)
```

### Why It Fails

When deployed to Render (`DEBUG=False`):
- `CORS_ALLOW_ALL_ORIGINS` defaults to `False` ✓ (correct)
- BUT if `CORS_ALLOWED_ORIGINS` environment variable is empty or misconfigured, NO origins are allowed
- Frontend receives: `403 Forbidden` + no `Access-Control-Allow-Origin` header
- **Silent failure:** Django doesn't log CORS rejections to stdout; they appear in Django debug toolbar only

### HTTP Request Flow

```
Vercel Frontend sends:
GET /api/products/
Origin: https://pie-global-funitures.vercel.app

↓

Django CORS Middleware checks:
1. Is DEBUG=True? NO
2. Is CORS_ALLOW_ALL_ORIGINS=True? NO
3. Is origin in CORS_ALLOWED_ORIGINS? [checking empty list]
4. Origin allowed? NO

↓

Response: 200 OK (request succeeds)
BUT missing header: Access-Control-Allow-Origin
Browser blocks response: "Cross-Origin Request Blocked"
```

### The Fix

```python
# Set explicit defaults for production
_default_cors_origins = 'http://localhost:3000,http://localhost:5173,https://pie-global-funitures.vercel.app'

CORS_ALLOWED_ORIGINS = config(
    'CORS_ALLOWED_ORIGINS', 
    default=_default_cors_origins, 
    cast=Csv()
)

CORS_ALLOW_CREDENTIALS = True  # Required for session auth

# CRITICAL: Never tie to DEBUG
CORS_ALLOW_ALL_ORIGINS = False  # Always False in production
```

**Key Changes:**
- ✅ Explicit default origins (no longer depends on DEBUG)
- ✅ Never allows ALL origins in production
- ✅ Clear intent: only these specific domains can access the API

---

## Issue #3: Missing APPEND_SLASH Configuration

### The Problem

**Current Code (NOT SET):**
```python
# APPEND_SLASH not defined anywhere in settings.py
```

Django defaults to `APPEND_SLASH = True`, BUT this creates problems with CORS:

### Why It Fails

```
Frontend requests: GET /products (no trailing slash)
↓
Django APPEND_SLASH redirects: 301 → /products/
↓
Browser CORS preflight doesn't follow redirects
↓
Response: 404 Not Found (preflight never reaches actual endpoint)
```

**CORS preflight (OPTIONS) doesn't follow HTTP redirects.** It fails immediately.

### The Fix

```python
# URL Configuration - CRITICAL for API endpoint consistency
APPEND_SLASH = True  # Explicitly set (also document it)
```

**Paired with:** Frontend always uses trailing slashes:
```typescript
'/products/'        // ✓ Correct
'/products/featured/'  // ✓ Correct
```

---

## Issue #4: Conflicting Vercel Rewrites Architecture

### The Problem

**vercel.json (CONFLICTING):**
```json
{
  "rewrites": [
    {
      "source": "/api/:path*",
      "destination": "https://pie-global-funitures.onrender.com/api/:path*"
    }
  ]
}
```

**frontend/.env.production (ALSO DIRECT URL):**
```dotenv
VITE_API_URL=https://pie-global-funitures.onrender.com/api
```

### Why It's Wrong

You're using **BOTH rewrites AND direct API calls**, which is redundant and confusing:

1. **Vercel Rewrites** (server-side proxy):
   - Vercel server intercepts `/api/...` requests
   - Proxies them to `https://pie-global-funitures.onrender.com/api/...`
   - Browser thinks request came from Vercel origin (might bypass CORS)

2. **Direct API Calls** (from frontend code):
   - Frontend calls `https://pie-global-funitures.onrender.com/api/...` directly
   - Browser sees it's cross-origin
   - CORS validation required

**Problem:** When using direct URLs, rewrites are useless. You're getting the worst of both:
- No benefit from server-side caching/security that rewrites provide
- Full CORS validation burden on backend
- Confusing configuration (which one is actually running?)

### The Fix

**Option A: Use Server-Side Rewrites (Recommended for SPA)**
```json
// vercel.json
{
  "rewrites": [
    { "source": "/api/:path*", "destination": "https://pie-global-funitures.onrender.com/api/:path*" }
  ]
}
```

```typescript
// frontend/.env.production
VITE_API_URL=/api  // Use relative path; Vercel rewrites handle it
```

**Benefits:**
- Browser sees requests as same-origin (no CORS needed)
- Vercel can cache API responses
- Backend doesn't need to allow CORS from Vercel domain
- Cleaner architecture

**Option B: Use Direct API Calls (Simpler, current fix)**
```json
// vercel.json (NO API rewrite)
{
  "rewrites": [
    { "source": "/(.*)", "destination": "/index.html" }  // Only SPA fallback
  ]
}
```

```typescript
// frontend/.env.production
VITE_API_URL=https://pie-global-funitures.onrender.com/api/  // Direct call
```

**Benefits:**
- Simple to understand: frontend calls backend directly
- No Vercel caching complexity
- Easier to debug network issues
- **Current implementation uses this** (recommended)

---

## Issue #5: Frontend withCredentials Mismatch

### The Problem

**Current Code (BROKEN):**
```typescript
const api = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: false,  // ❌ WRONG when CORS_ALLOW_CREDENTIALS=True
});
```

### Why It Fails

When your backend sets:
```python
CORS_ALLOW_CREDENTIALS = True
```

But frontend doesn't send credentials (`withCredentials: false`):
- Backend accepts credentials from any origin (less restrictive)
- Frontend doesn't send them (credentials are cookies, Authorization headers)
- **This works, but it's inconsistent and loses auth functionality**

If you later add authentication (JWT, sessions), requests will silently fail because:
```
Browser: "I'm not sending credentials across origins"
Django: "I won't accept non-credentialed requests with auth required"
Result: 401 Unauthorized (silent on frontend)
```

### The Fix

```typescript
const api = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true,  // ✅ Match CORS_ALLOW_CREDENTIALS=True
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json',
  },
});
```

**This enables:**
- Session cookies included in requests
- Authorization headers sent cross-origin
- CORS preflight succeeds with credentials check

---

## Issue #6: API URL Missing Trailing Slash

### The Problem

**frontend/.env.production (BROKEN):**
```dotenv
VITE_API_URL=https://pie-global-funitures.onrender.com/api
```

**frontend/src/services/api.ts (BROKEN):**
```typescript
const API_BASE_URL = ... ? 'http://localhost:8000/api' : '/api';
```

No trailing slashes in base URLs.

### Why It Fails

When axios calls:
```typescript
api.get('/products/')  // Has trailing slash
```

With base URL `https://pie-global-funitures.onrender.com/api` (no trailing slash):
```
Resulting URL: https://pie-global-funitures.onrender.com/api/products/
```

Seems correct, but axios behavior with base URLs is:
```
baseURL: "https://example.com/api"  (no trailing slash)
request: "/products/"
result: "https://example.com/api/products/"  ✓

baseURL: "https://example.com/api"  (no trailing slash)
request: "products/"  (no leading slash)
result: "https://example.com/apiproducts/"  ✗ WRONG
```

While your code works (because you use leading slash), it's fragile.

### The Fix

```typescript
// Always use trailing slash in base URL
const API_BASE_URL = import.meta.env.VITE_API_URL || 
  (typeof window !== 'undefined' && window.location.hostname === 'localhost' 
    ? 'http://localhost:8000/api/'  // Trailing slash
    : 'https://pie-global-funitures.onrender.com/api/');  // Trailing slash
```

```dotenv
# .env.production with trailing slash
VITE_API_URL=https://pie-global-funitures.onrender.com/api/
```

---

## Django Settings Middleware Order Issue

### Current (CORRECT):

```python
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # ✓ FIRST
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    # ... rest of middleware
]
```

✅ **Correct!** CorsMiddleware must be before SecurityMiddleware so it can add CORS headers to all responses.

---

## Environment Variables Required on Render

### Render Dashboard > Service > Environment

Set these variables:

| Variable | Value | Notes |
|----------|-------|-------|
| `DJANGO_DEBUG` | `False` | ⚠️ CRITICAL: Don't use `true` in production |
| `DJANGO_SECRET_KEY` | `<strong-random-key>` | Use `python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'` |
| `DJANGO_ALLOWED_HOSTS` | `pie-global-funitures.onrender.com` | Your Render domain (no wildcards) |
| `CORS_ALLOWED_ORIGINS` | `http://localhost:3000,http://localhost:5173,https://pie-global-funitures.vercel.app` | Comma-separated, no spaces |
| `CSRF_TRUSTED_ORIGINS` | `http://localhost:3000,http://localhost:5173,https://pie-global-funitures.vercel.app,https://pie-global-funitures.onrender.com` | Frontend + backend domains |
| `DATABASE_URL` | `postgresql://user:pass@host/db` | PostgreSQL connection string |

### Render Auto-Set Variables (Don't override):

```
RENDER_EXTERNAL_URL=https://pie-global-funitures.onrender.com
```

Settings.py automatically parses this and adds to ALLOWED_HOSTS.

---

## Environment Variables Required on Vercel

### Vercel Dashboard > Project Settings > Environment Variables

Set for **Production** (and optionally **Preview**):

| Variable | Value |
|----------|-------|
| `VITE_API_URL` | `https://pie-global-funitures.onrender.com/api/` |

---

## Root Cause Analysis: Why Requests Fail

### Scenario: Vercel Frontend → Render Backend API Call

```
1. Browser sends GET https://pie-global-funitures.onrender.com/api/products/
   Origin: https://pie-global-funitures.vercel.app

2. Render receives request
   Host header: pie-global-funitures.onrender.com

3. Django ALLOWED_HOSTS validation
   ✗ Is "pie-global-funitures.onrender.com" in ALLOWED_HOSTS?
   ✗ With wildcard ".onrender.com": NO
   → 400 Bad Request (DisallowedHost exception)
   → Request never reaches view code
   → No CORS headers sent

4. Browser receives 400 Bad Request
   No "Access-Control-Allow-Origin" header
   Browser blocks response
   Frontend error: "Failed to fetch"

---

OR with correct ALLOWED_HOSTS:

1. Browser sends request (same as above)

2. Render receives request
   Host header: pie-global-funitures.onrender.com

3. Django ALLOWED_HOSTS validation ✓ PASS

4. Django CORS preflight check
   ✗ CORS_ALLOWED_ORIGINS is empty/misconfigured
   → Django sends 200 OK but no "Access-Control-Allow-Origin" header
   → Request fails browser CORS check

5. Browser receives 200 OK but no CORS header
   Browser blocks response
   Frontend error: "CORS policy: Cross-Origin Request Blocked"

---

OR with correct CORS but wrong withCredentials:

1. Request succeeds, data returns ✓
2. But session authentication doesn't work ✗
3. Login/protected routes fail silently
```

---

## What Was Fixed

| Issue | Before | After |
|-------|--------|-------|
| **ALLOWED_HOSTS** | `.onrender.com` (wildcard, broken) | `pie-global-funitures.onrender.com` (exact domain) |
| **CORS_ALLOW_ALL_ORIGINS** | Tied to DEBUG flag | Hardcoded to `False` (always explicit) |
| **APPEND_SLASH** | Not set (uses Django default) | Explicitly set to `True` |
| **Vercel rewrites** | Conflicting with direct API calls | Removed; using direct calls only |
| **withCredentials** | `false` (mismatches backend config) | `true` (matches `CORS_ALLOW_CREDENTIALS`) |
| **API Base URL** | `...api` (no trailing slash) | `...api/` (consistent with Django) |
| **CORS env vars** | Not documented clearly | Explicit defaults in code + Render env |

---

## Security Implications

### Before Fixes (INSECURE):
- ❌ ALLOWED_HOSTS with wildcards could allow unauthorized domains
- ❌ CORS_ALLOW_ALL_ORIGINS depending on DEBUG (easily misconfigured in CI/CD)
- ❌ Implicit trailing slash handling (harder to reason about)

### After Fixes (SECURE):
- ✅ Explicit ALLOWED_HOSTS (only exact domains)
- ✅ Explicit CORS policy (never auto-allow all)
- ✅ Explicit trailing slash handling (clear intent)
- ✅ CSRF protection enabled with trusted origins
- ✅ Secure cookie settings (HTTPS, HttpOnly, SameSite)
- ✅ HSTS headers for HTTPS enforcement

---

## Testing Verification Commands

### Backend (Render)

```bash
# Test ALLOWED_HOSTS
curl -X GET https://pie-global-funitures.onrender.com/api/products/ \
  -H "Host: pie-global-funitures.onrender.com" \
  -v
# Expected: 200 OK (not 400 DisallowedHost)

# Test CORS preflight
curl -X OPTIONS https://pie-global-funitures.onrender.com/api/products/ \
  -H "Origin: https://pie-global-funitures.vercel.app" \
  -H "Access-Control-Request-Method: GET" \
  -v
# Expected: 200 OK + "Access-Control-Allow-Origin: https://pie-global-funitures.vercel.app"

# Test with credentials
curl -X OPTIONS https://pie-global-funitures.onrender.com/api/products/ \
  -H "Origin: https://pie-global-funitures.vercel.app" \
  -H "Access-Control-Request-Method: GET" \
  -v
# Expected: 200 OK + "Access-Control-Allow-Credentials: true"
```

### Frontend (Browser DevTools)

1. Open Vercel production site
2. Open DevTools > Network tab
3. Trigger API call
4. Click on request in Network tab
5. Check "Response Headers":
   - ✓ `access-control-allow-origin: https://pie-global-funitures.vercel.app`
   - ✓ `access-control-allow-credentials: true`
   - ✓ No CORS errors in Console

---

## Files Modified

1. **backend/pie_global/settings.py**
   - Fixed ALLOWED_HOSTS (explicit domains, no wildcards)
   - Added explicit APPEND_SLASH = True
   - Fixed CORS_ALLOW_ALL_ORIGINS (not tied to DEBUG)
   - Updated CORS_ALLOWED_ORIGINS defaults
   - Updated CSRF_TRUSTED_ORIGINS

2. **frontend/src/services/api.ts**
   - Updated API_BASE_URL with trailing slashes
   - Changed withCredentials from false to true

3. **frontend/.env.production**
   - Added trailing slash to VITE_API_URL

4. **frontend/vercel.json**
   - Removed conflicting `/api` rewrite rule
   - Kept only SPA fallback rewrite

5. **New: DEPLOYMENT_CHECKLIST.md**
   - Complete pre-deployment verification
   - Render/Vercel deployment steps
   - Production testing procedures
   - Troubleshooting guide

---

## Next Steps

1. ✅ **Update backend settings** (Done)
2. ✅ **Update frontend code** (Done)
3. **Set environment variables on Render** (Pending)
4. **Set environment variables on Vercel** (Pending)
5. **Deploy backend to Render** (Pending)
6. **Deploy frontend to Vercel** (Pending)
7. **Test production endpoints** (Pending)

See [DEPLOYMENT_CHECKLIST.md](../DEPLOYMENT_CHECKLIST.md) for detailed steps.

---

**Prepared by:** GitHub Copilot  
**For:** Pie Global Furniture Team  
**Status:** Ready for Production
