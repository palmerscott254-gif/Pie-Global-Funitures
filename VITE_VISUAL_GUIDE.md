# VITE_API_URL Fix - Visual Explanation

## The Problem

```
┌─────────────────────────────────────────────┐
│         Vercel Production Build             │
│                                             │
│  1. npm run build                           │
│  2. VITE_API_URL = undefined               │
│  3. Fallback: "localhost?" → NO             │
│  4. Uses hardcoded URL                      │
│  5. If wrong → Silent failure ✗             │
└─────────────────────────────────────────────┘

   ↓

┌─────────────────────────────────────────────┐
│      Browser (Vercel Frontend)              │
│                                             │
│  import.meta.env.VITE_API_URL = undefined   │
│  Falls back to hardcoded URL                │
│  Requests to wrong backend                  │
│  → 404 Not Found ✗                          │
│  → CORS errors ✗                           │
│  → Silent API failures ✗                    │
└─────────────────────────────────────────────┘
```

---

## The Solution

```
┌─────────────────────────────────────────────┐
│       vite.config.ts (NEW)                  │
│                                             │
│  define: {                                  │
│    VITE_API_URL: process.env.VITE_API_URL   │
│  }                                          │
│                                             │
│  Ensures env var is available at build      │
└─────────────────────────────────────────────┘

   ↓↓↓

┌─────────────────────────────────────────────┐
│       api.ts (IMPROVED)                     │
│                                             │
│  const getApiUrl = () => {                  │
│    // Priority 1: Env var                   │
│    // Priority 2: Local detection           │
│    // Priority 3: Fallback                  │
│  }                                          │
│                                             │
│  Smart detection with fallbacks             │
│  Console logging for debugging              │
│  Clear error messages                       │
└─────────────────────────────────────────────┘

   ↓↓↓

┌─────────────────────────────────────────────┐
│      Vercel Environment Variables           │
│                                             │
│  VITE_API_URL=                              │
│    https://pie-global-funitures.onrender..  │
│                                             │
│  Set in Project Settings                    │
└─────────────────────────────────────────────┘

   ↓↓↓

┌─────────────────────────────────────────────┐
│      Browser (Vercel Frontend)              │
│                                             │
│  import.meta.env.VITE_API_URL =             │
│    'https://pie-global-funitures.onrender'  │
│                                             │
│  Requests to correct backend                │
│  → 200 OK ✓                                 │
│  → CORS headers present ✓                   │
│  → API data loads ✓                         │
│                                             │
│  Console: [API Configuration] ...log...     │
└─────────────────────────────────────────────┘
```

---

## Priority System (How It Works)

### Development

```
┌─ npm run dev
│
├─ Check .env: VITE_API_URL=http://localhost:8000/api/
│
├─ getApiUrl() Priority 1: Is VITE_API_URL set?
│  └─ YES → Return: http://localhost:8000/api/
│
├─ Console logs: [API Configuration] Using API URL: http://localhost:8000/api/
│
└─ ✓ All API calls go to local backend
```

### Production (Vercel)

```
┌─ vercel deploy
│
├─ Read Vercel env vars: VITE_API_URL=https://pie-global...onrender.com/api/
│
├─ vite build with define option
│  └─ Hardcode VITE_API_URL into dist/index.html
│
├─ Deployed to Vercel CDN
│
├─ Browser loads page
│
├─ getApiUrl() Priority 1: Is VITE_API_URL set?
│  └─ YES → Return: https://pie-global...onrender.com/api/
│
└─ ✓ All API calls go to Render backend
```

---

## Fallback Chain

```
                        ┌──────────────────┐
                        │ Vercel Env Vars  │
                        │ VITE_API_URL=... │
                        └────────┬─────────┘
                                 │
                                 ↓
                    ┌─────────────────────────┐
                    │  API URL in build       │
                    │  (from env var)         │
                    └────────┬────────────────┘
                             │
                             ↓
        ┌────────────────────────────────────────┐
        │ Priority 1: Build-time env var         │
        │ (import.meta.env.VITE_API_URL)        │
        └────────┬───────────────────────────────┘
                 │
        ✓ Success? Return immediately
        ✗ Undefined? Continue to Priority 2
                 │
                 ↓
        ┌────────────────────────────────────────┐
        │ Priority 2: Local environment detection│
        │ (is localhost/private IP?)             │
        └────────┬───────────────────────────────┘
                 │
        ✓ Is local? Return http://localhost:8000/api/
        ✗ Not local? Continue to Priority 3
                 │
                 ↓
        ┌────────────────────────────────────────┐
        │ Priority 3: Production fallback         │
        │ https://pie-global...onrender.com/api/ │
        └────────┬───────────────────────────────┘
                 │
                 ↓
        ┌────────────────────────────────────────┐
        │ Final API_BASE_URL determined          │
        │ Ready for API calls                    │
        └────────────────────────────────────────┘
```

---

## Before vs After Comparison

### BEFORE (Broken Logic)

```typescript
const API_BASE_URL = 
  import.meta.env.VITE_API_URL ||              // ← Often undefined
  (typeof window !== 'undefined' &&
   window.location.hostname === 'localhost'     // ← Too specific
     ? 'http://localhost:8000/api/'
     : 'https://pie-global-funitures.onrender.com/api/');

// On Vercel:
// - VITE_API_URL is undefined (not in env vars)
// - hostname is 'pie-global-funitures.vercel.app' (NOT 'localhost')
// - Falls back to hardcoded URL
// - No visibility into what URL is being used
// - Silent failure if hardcoded URL wrong
```

### AFTER (Improved Logic)

```typescript
const getApiUrl = (): string => {
  // Explicitly check if env var exists
  const envUrl = import.meta.env.VITE_API_URL;
  if (envUrl && typeof envUrl === 'string' && envUrl.trim()) {
    return envUrl;  // ← Explicit, not relying on fallback
  }

  // Better local detection
  if (typeof window !== 'undefined') {
    const isLocal =
      window.location.hostname === 'localhost' ||
      window.location.hostname === '127.0.0.1' ||
      window.location.hostname.startsWith('192.168.') ||
      window.location.hostname.startsWith('10.');
    if (isLocal) return 'http://localhost:8000/api/';
  }

  // Final fallback
  return 'https://pie-global-funitures.onrender.com/api/';
};

const API_BASE_URL = getApiUrl();

// Add debug logging
if (import.meta.env.DEV) {
  console.debug('[API Configuration] Using:', API_BASE_URL);
}

// Clear error message
if (!isValidApiUrl(API_BASE_URL)) {
  throw new Error(`Invalid API URL: "${API_BASE_URL}". Check VITE_API_URL env var.`);
}
```

---

## Data Flow

### Development Flow

```
Developer
    │
    ├─ npm run dev
    │
    ├─ Reads .env: VITE_API_URL=http://localhost:8000/api/
    │
    ├─ Frontend starts on http://localhost:3000
    │
    ├─ Browser console: [API Configuration] Using API URL: http://localhost:8000/api/
    │
    ├─ Click "Products" button
    │
    ├─ Frontend calls: api.get('/products/')
    │
    ├─ Actual request: GET http://localhost:8000/api/products/
    │
    ├─ Backend responds: 200 OK + JSON data
    │
    └─ ✓ Products display on page
```

### Production Flow

```
User
    │
    ├─ Visit https://pie-global-funitures.vercel.app
    │
    ├─ Vercel serves dist/index.html (with VITE_API_URL hardcoded)
    │
    ├─ Browser loads JavaScript
    │
    ├─ getApiUrl() called:
    │  ├─ Check import.meta.env.VITE_API_URL
    │  ├─ Found: https://pie-global-funitures.onrender.com/api/
    │  └─ Return immediately
    │
    ├─ Click "Products" button
    │
    ├─ Frontend calls: api.get('/products/')
    │
    ├─ Actual request: GET https://pie-global-funitures.onrender.com/api/products/
    │
    ├─ Backend responds: 200 OK + JSON data
    │
    └─ ✓ Products display on page
```

---

## Vercel Environment Variable Setup

```
┌─────────────────────────────────────────────┐
│  Vercel Dashboard                           │
│  ┌───────────────────────────────────────┐  │
│  │ Your Project                          │  │
│  │  └─ Project Settings                  │  │
│  │     └─ Environment Variables          │  │
│  │        ├─ Name: VITE_API_URL          │  │
│  │        ├─ Value: https://pie-global..│  │
│  │        └─ Scope: Production           │  │
│  │                                       │  │
│  │  Then: Redeploy Project               │  │
│  └───────────────────────────────────────┘  │
│                                             │
│  ↓                                          │
│                                             │
│  Next Deploy:                               │
│  ├─ Read VITE_API_URL from env vars         │
│  ├─ Pass to vite build                      │
│  ├─ Hardcode into dist/index.html           │
│  └─ Deploy to CDN                           │
└─────────────────────────────────────────────┘
```

---

## Status Dashboard

```
┌──────────────────────┬─────────────────────────┐
│ Component            │ Status                  │
├──────────────────────┼─────────────────────────┤
│ vite.config.ts       │ ✅ Updated              │
│ api.ts               │ ✅ Updated              │
│ .env                 │ ✅ Updated              │
│ .env.production      │ ✅ Updated              │
│ Vercel env var       │ ⏳ Action Required       │
│ Git commit           │ ⏳ Action Required       │
│ Git push             │ ⏳ Action Required       │
│ Vercel build         │ ⏳ Awaiting push        │
│ Production test      │ ⏳ Awaiting deploy      │
└──────────────────────┴─────────────────────────┘

Next Step: Set VITE_API_URL in Vercel
```

---

## Summary

```
┌─────────────────────────────────────────────────┐
│  BEFORE                    │  AFTER              │
├─────────────────────────────────────────────────┤
│ Env var often undefined    │ Always available    │
│ Unsafe fallback logic      │ Smart detection     │
│ Silent failures            │ Debug logging       │
│ Hard to troubleshoot       │ Clear error msgs    │
│ Vercel env var ignored     │ Vercel env var used │
│                            │                     │
│ ❌ Production broken       │ ✅ Production ready │
└─────────────────────────────────────────────────┘
```

---

**Status:** ✅ Ready for Deployment  
**Time to Deploy:** 10 minutes  
**Risk:** Low  
**Impact:** High (fixes production failures)
