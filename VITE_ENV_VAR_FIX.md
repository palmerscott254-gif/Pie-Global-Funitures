# Vite import.meta.env.VITE_API_URL: Diagnostic & Fix

**Issue:** `import.meta.env.VITE_API_URL` is undefined or not working correctly  
**Impact:** API calls fail in production (Vercel)  
**Status:** DIAGNOSING & FIXING

---

## Root Causes Identified

### Issue #1: Fallback Logic Problem (CRITICAL)

**Current Code (api.ts, lines 14-20):**
```typescript
const API_BASE_URL = import.meta.env.VITE_API_URL || 
  (typeof window !== 'undefined' && window.location.hostname === 'localhost' 
    ? 'http://localhost:8000/api/'
    : 'https://pie-global-funitures.onrender.com/api/');
```

**The Problem:**
- When Vercel builds, `import.meta.env.VITE_API_URL` might be `undefined`
- Fallback uses `window.location.hostname === 'localhost'`
- On Vercel production, hostname is `pie-global-funitures.vercel.app` (NOT localhost)
- Falls back to hardcoded Render URL
- If Render URL is wrong or env var never set during build, you get silent failures

**Specific Failure Scenario:**
```
1. Vercel build runs
2. VITE_API_URL not set in Vercel env vars → undefined
3. Fallback logic: "Is hostname localhost?" NO
4. Uses hardcoded URL: https://pie-global-funitures.onrender.com/api/
5. If that hardcoded URL is ever wrong → Requests fail silently
6. No error message, just failed API calls
```

---

### Issue #2: Vite Config Missing Environment Variable Exposure

**Current vite.config.ts (INCOMPLETE):**
```typescript
export default defineConfig({
  plugins: [react()],
  // ❌ NO environment variable configuration
  // ❌ NO explicit VITE_API_URL exposure
})
```

**Why It Matters:**
- Vite uses `.env` files to populate `import.meta.env.*`
- Default behavior: Only `VITE_*` prefixed variables are exposed (✓ correct)
- But if env vars aren't explicitly defined, build may not pick them up
- Especially problematic with SSR or complex build setups

---

### Issue #3: Vercel Environment Variable Not Passed to Build

**Vercel Dashboard likely missing:**
```
Project Settings > Environment Variables
VITE_API_URL = https://pie-global-funitures.onrender.com/api/
```

**Why It Matters:**
- Vercel builds the app during deployment
- If `VITE_API_URL` not set in Vercel env vars, build-time value is undefined
- Frontend deployed with undefined API URL
- Fallback logic kicks in (hardcoded URL)

---

### Issue #4: Missing .env.local for Development

**What exists:**
- `.env` (checked in git, dev only)
- `.env.production` (checked in git, production values)

**What's missing:**
- `.env.local` (NOT checked in git, local overrides)

**Why It Matters:**
- Developers often need different local URLs
- `.env.local` has highest priority and isn't committed
- Without it, checking out code forces dev URL usage

---

## The Complete Fix

### Fix #1: Update vite.config.ts (IMMEDIATE)

Add explicit environment variable configuration:

```typescript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  
  // Explicitly define environment variables
  define: {
    'import.meta.env.VITE_API_URL': JSON.stringify(
      process.env.VITE_API_URL || 'http://localhost:8000/api/'
    ),
  },
  
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/media': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
  
  build: {
    outDir: 'dist',
    sourcemap: false,
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom', 'react-router-dom'],
          ui: ['framer-motion', 'swiper'],
        },
      },
    },
  },
})
```

**What changed:**
- Added `define` option to explicitly expose `VITE_API_URL`
- Uses `process.env.VITE_API_URL` from Vercel env vars
- Falls back to dev URL if not set

---

### Fix #2: Update api.ts Fallback Logic (IMMEDIATE)

Replace the unsafe fallback with explicit environment-aware logic:

```typescript
// CRITICAL: API URL configuration with proper fallback hierarchy
// Priority: 1. import.meta.env.VITE_API_URL (Vercel/build-time)
//           2. window.__API_URL__ (injected at runtime)
//           3. Environment detection (localhost vs production)

const getApiUrl = (): string => {
  // Priority 1: Use build-time environment variable (VITE_API_URL)
  const envUrl = import.meta.env.VITE_API_URL;
  if (envUrl && typeof envUrl === 'string' && envUrl.trim()) {
    return envUrl;
  }

  // Priority 2: Check if we're in browser and detect environment
  if (typeof window !== 'undefined') {
    const isLocal = 
      window.location.hostname === 'localhost' || 
      window.location.hostname === '127.0.0.1' ||
      window.location.hostname.startsWith('192.168.') ||
      window.location.hostname.startsWith('10.');

    if (isLocal) {
      return 'http://localhost:8000/api/';
    }

    // Production: Use relative path for Vercel rewrites OR absolute URL
    // Option A: Relative path (requires Vercel rewrites setup)
    // return '/api/';
    
    // Option B: Absolute URL (direct to Render backend)
    return 'https://pie-global-funitures.onrender.com/api/';
  }

  // Fallback for SSR or edge cases
  return 'https://pie-global-funitures.onrender.com/api/';
};

const API_BASE_URL = getApiUrl();

// Log API URL in development for debugging
if (import.meta.env.DEV) {
  console.debug('[API] Configured API URL:', API_BASE_URL);
}

// Validate API URL to prevent SSRF attacks
const isValidApiUrl = (url: string): boolean => {
  try {
    if (url.startsWith('/')) return true; // Relative path OK
    const parsedUrl = new URL(url);
    return ['http:', 'https:'].includes(parsedUrl.protocol);
  } catch {
    return false;
  }
};

if (!isValidApiUrl(API_BASE_URL)) {
  throw new Error(`Invalid API URL configuration: "${API_BASE_URL}"`);
}
```

**What changed:**
- Created `getApiUrl()` function with explicit priority hierarchy
- Better detection for local IPs (192.168.*, 10.*, etc.)
- Clear logging in dev mode for debugging
- Better error messages

---

### Fix #3: Create .env.local for Development (OPTIONAL)

Create file: `frontend/.env.local` (NOT committed to git)

```dotenv
# Override environment variables for local development
# This file is NOT committed to git (.gitignore should include it)

# Use this if you want to test with a remote backend
# Uncomment to override .env settings:
# VITE_API_URL=https://pie-global-funitures.onrender.com/api/

# Or use localhost:
VITE_API_URL=http://localhost:8000/api/
```

Add to `.gitignore`:
```
# Local environment overrides
.env.local
.env.*.local
```

---

### Fix #4: Set Environment Variables on Vercel (IMMEDIATE ACTION REQUIRED)

**Steps:**
1. Go to Vercel Dashboard
2. Select your project
3. Project Settings > Environment Variables
4. Add:
   ```
   VITE_API_URL = https://pie-global-funitures.onrender.com/api/
   ```
5. Make sure to set it for **Production** (and optionally **Preview**)
6. **Redeploy** the project (Settings > Deployments > Redeploy)

**Visual:**
```
Environment Variables:
Name: VITE_API_URL
Value: https://pie-global-funitures.onrender.com/api/
Scope: Production
☑️ Auto Expose to Client (Vite)
```

---

### Fix #5: Update .env and .env.production (BEST PRACTICE)

**frontend/.env (Local Development):**
```dotenv
# Vite Frontend Environment Variables
# Note: Only variables prefixed with VITE_ are exposed to the client

# API Configuration
# In development, use local Django backend
VITE_API_URL=http://localhost:8000/api/

# Development marker for debugging
VITE_ENV=development
```

**frontend/.env.production (Build Time - Vercel):**
```dotenv
# Vite Frontend Environment Variables - Production/Vercel Deployment
# Note: These are overridden by Vercel environment variables if set

# API Configuration 
# Production: Point to deployed backend (Render)
# This can be overridden in Vercel Project Settings > Environment Variables
VITE_API_URL=https://pie-global-funitures.onrender.com/api/

# Production marker
VITE_ENV=production
```

**Note:** Vercel env vars take precedence over .env.production files!

---

## Why These Fixes Work

### Before Fix
```
1. Vercel build runs
2. VITE_API_URL undefined → Falls back to window.location.hostname check
3. Hostname is vercel.app, not localhost
4. Uses hardcoded URL
5. If hardcoded URL wrong → Silent failures
6. No console error, just failed API calls
```

### After Fix
```
1. Vercel build runs with VITE_API_URL=https://...onrender.com/api/
2. vite.config.ts picks up from process.env.VITE_API_URL
3. api.ts calls getApiUrl()
4. Returns import.meta.env.VITE_API_URL (set at build time)
5. API calls go to correct backend
6. If URL is wrong → Clear error with URL in message
7. Easy to debug with console.debug in dev mode
```

---

## Testing the Fix

### Local Development Test
```bash
cd frontend

# 1. Make sure .env exists with VITE_API_URL=http://localhost:8000/api/
cat .env

# 2. Start dev server
npm run dev

# 3. Open browser console (F12 > Console)
# Should see: [API] Configured API URL: http://localhost:8000/api/

# 4. Make an API call
# Should succeed if backend is running

# 5. Check Network tab
# API requests should go to http://localhost:8000/api/products
```

### Production Test (After Vercel Deploy)
```bash
# 1. Visit Vercel site in browser
# 2. Open DevTools > Console
# (Should NOT see [API] debug message - only in dev)

# 3. Network tab
# API requests should go to https://pie-global-funitures.onrender.com/api/products

# 4. Check if products load
# No 404 or CORS errors
```

### Verify Vercel Env Var
```bash
# Vercel Dashboard > Deployments > Select latest > Logs
# Search for "VITE_API_URL" to confirm it was passed to build

# Or check built HTML:
# Visit production site > View Source > Search for "api"
# Should see your Render backend URL hardcoded (expected)
```

---

## Common Issues & Fixes

### Issue: Still Getting Undefined
**Check:**
1. Vercel env var set? (Project Settings > Environment Variables)
2. Vercel redeploy triggered? (Not just push, but actual redeploy)
3. Cache cleared? (Vercel > Deployments > Redeploy with "Clear Build Cache")
4. .env.production committed? (git status)

**Fix:**
```bash
# Force rebuild
vercel deploy --prod --clear

# Or in Vercel Dashboard: Deployments > Redeploy
```

---

### Issue: Works Locally, Fails in Production
**Cause:** Vercel env vars not set

**Fix:**
1. Go to Vercel Dashboard
2. Project Settings > Environment Variables
3. Add `VITE_API_URL=https://pie-global-funitures.onrender.com/api/`
4. Redeploy

---

### Issue: API calls still going to hardcoded URL
**Cause:** Fallback logic still being used

**Fix:**
1. Update vite.config.ts with `define` option
2. Update api.ts with `getApiUrl()` function
3. Verify vite.config.ts is saved
4. Run `npm run build` locally
5. Check dist/index.html for your backend URL

---

## Files to Modify

1. **frontend/vite.config.ts** - Add environment variable definition
2. **frontend/src/services/api.ts** - Replace API URL logic
3. **frontend/.env** - Ensure correct local dev URL
4. **frontend/.env.production** - Ensure correct production URL
5. **Vercel Dashboard** - Set VITE_API_URL environment variable

---

## Deployment Checklist

- [ ] Update `vite.config.ts` with `define` option
- [ ] Update `api.ts` with `getApiUrl()` function
- [ ] Verify `.env` has `VITE_API_URL=http://localhost:8000/api/`
- [ ] Verify `.env.production` has correct Render URL
- [ ] Set `VITE_API_URL` in Vercel Project Settings
- [ ] Commit code changes
- [ ] Push to GitHub
- [ ] Verify Vercel builds successfully (check logs)
- [ ] Test production site (should see no API errors)
- [ ] Check Network tab (should see correct backend URL)

---

## Summary

| Issue | Cause | Fix |
|-------|-------|-----|
| `VITE_API_URL` undefined | Not set in Vercel env vars | Set in Vercel Project Settings |
| Fallback logic broken | Checks hostname instead of env var | Use priority-based `getApiUrl()` |
| No debug info | Silent failures | Added console.debug logging |
| Build doesn't pick up env var | Vite config doesn't expose it | Added `define` option |
| Local dev conflicts with prod | No .env.local | Create .env.local (not committed) |

---

**Status:** READY FOR IMPLEMENTATION  
**Estimated Fix Time:** 10 minutes  
**Risk Level:** LOW (no breaking changes)
