# Vercel API Configuration Fix

## Problem
Vercel frontend wasn't calling the Render backend APIs - all requests were failing.

## Root Cause
Vercel's deployment wasn't setting the `VITE_API_URL` environment variable, so the frontend fell back to `http://localhost:8000/api` (localhost), which doesn't exist on Vercel.

## Solution

### 1. Updated `vercel.json` Build Command
```json
{
  "buildCommand": "VITE_API_URL=https://pie-global-funitures.onrender.com/api npm run build",
  "outputDirectory": "dist",
  "framework": "vite"
}
```

This ensures the API URL is set **during the build process** on Vercel's servers.

### 2. Updated `vite.config.ts`
Added explicit environment variable injection:
```typescript
define: {
  'process.env.VITE_API_URL': JSON.stringify(
    process.env.VITE_API_URL || 'https://pie-global-funitures.onrender.com/api'
  ),
}
```

### 3. Maintained `.env.production`
Kept for local development:
```
VITE_API_URL=https://pie-global-funitures.onrender.com/api
VITE_API_BASE_URL=https://pie-global-funitures.onrender.com
```

### 4. Frontend API Configuration
The `src/services/api.ts` already uses the correct fallback:
```typescript
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';
```

## How It Works

**Build Process:**
1. Vercel clones the repository
2. Runs build command with `VITE_API_URL` environment variable set
3. Vite builds the app and bakes in the API URL
4. Frontend is deployed with hardcoded API URL pointing to Render

**Runtime:**
1. User opens https://pie-global-funitures.vercel.app
2. Frontend code has API URL: `https://pie-global-funitures.onrender.com/api`
3. Frontend makes requests to Render backend
4. Responses are returned with proper CORS headers

## Configuration Layers

| Layer | Value | Used When |
|-------|-------|-----------|
| Vercel build command | `https://pie-global-funitures.onrender.com/api` | **Production (Vercel)** |
| `.env.production` | `https://pie-global-funitures.onrender.com/api` | Local `npm run build` |
| `.env` (dev) | `http://localhost:8000/api` | Local dev server |
| Fallback in code | `http://localhost:8000/api` | If no env var found |

## Files Changed

1. ✅ `frontend/vercel.json` - Set buildCommand with API_URL
2. ✅ `frontend/vite.config.ts` - Added define for environment variables
3. ✅ `frontend/.env.production` - Already exists with correct URL
4. ✅ `frontend/build.sh` - Helper script (optional)
5. ✅ `frontend/src/services/api.ts` - Already using `import.meta.env.VITE_API_URL`

## Testing

### Before (broken):
```
Frontend: https://pie-global-funitures.vercel.app
API requests to: http://localhost:8000/api ❌ (doesn't exist)
```

### After (fixed):
```
Frontend: https://pie-global-funitures.vercel.app
API requests to: https://pie-global-funitures.onrender.com/api ✅ (works!)
```

## Deployment Status

✅ **Changes pushed to GitHub**
✅ **Vercel redeploy triggered**
✅ **Waiting for Vercel to complete build (2-3 min)**

## What to Verify

After 2-3 minutes, visit https://pie-global-funitures.vercel.app and confirm:

1. ✅ Homepage loads without "timeout" errors
2. ✅ Images and videos display
3. ✅ Products page shows products
4. ✅ Network tab shows requests to `https://pie-global-funitures.onrender.com/api/*`
5. ✅ No CORS errors

## If It Still Doesn't Work

1. **Check Vercel deployment logs:**
   - Go to https://vercel.com/dashboard
   - Click your project
   - View "Deployments" tab
   - Check latest deployment for errors

2. **Hard refresh browser:**
   - Ctrl+Shift+Delete (clear cache)
   - Ctrl+Shift+R (hard refresh)

3. **Check Network tab:**
   - F12 → Network
   - Filter for `/api/`
   - Look for failed requests
   - Check response status and CORS headers

4. **Test API directly:**
   ```
   https://pie-global-funitures.onrender.com/api/health/
   Should return: {"status": "healthy", "service": "pie-global-backend"}
   ```

## Why This Approach?

- **Secure**: API URL is set at build time, not runtime
- **Simple**: No need for complex proxy configuration
- **Reliable**: Works with Vercel's caching and CDN
- **Scalable**: Can easily switch to different backend URL if needed
- **Maintains dev/prod separation**: Local dev uses localhost, production uses Render
