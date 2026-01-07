# Quick Start: User Authentication Testing

## Prerequisites
- Backend running: `python manage.py runserver`
- PostgreSQL connected and migrated
- Frontend dev server running (optional for API testing)

## Quick Test Steps

### Step 1: Test Backend Registration
Open `auth-test.html` in your browser:
1. Fill in Name, Email, Password, Confirm Password
2. Click "Register"
3. Should see success response with user data

**What happens**:
- Password hashed with PBKDF2-SHA256
- User stored in PostgreSQL `users` table
- Session cookie created
- Frontend localStorage updated (for UI state)

### Step 2: Verify Database
Check PostgreSQL to confirm user exists:

```bash
# Connect to your database
psql -U postgres -d pie_global_db

# Query users table
SELECT id, name, email, created_at FROM users;
```

You should see your new account!

### Step 3: Test Login
In `auth-test.html`:
1. Fill Email and Password with your registered credentials
2. Click "Login"
3. Should see success response

### Step 4: Test Current User
Click "Get Current User" button
- Shows logged-in user's info if authenticated
- Shows error if not authenticated

### Step 5: Test Logout
Click "Logout" button
- Session destroyed
- "Get Current User" will fail after this

## Frontend Integration

### Register Page (`/register`)
- Submits to `POST /api/auth/users/register/`
- Shows validation errors (password mismatch, duplicate email)
- Stores user info in localStorage for header display
- Redirects to home or intended page on success

### Login Page (`/login`)
- Submits to `POST /api/auth/users/login/`
- Shows authentication errors (wrong password, account not found)
- Creates session on successful login
- Redirects to home or intended page

### Header/Navigation
- Checks `localStorage.getItem('pgf-auth-current')` for user info
- Shows "Sign out" button when authenticated
- Shows "Sign in" / "Create account" links when not authenticated
- Updates when `pgf-auth-changed` event fires

## Important Notes

### Session vs localStorage
- **Session** (backend): Created on `/login` and `/register`
- **localStorage** (frontend): Updated with user email/name/id for UI state
- Both must work together - session authenticates requests, localStorage displays in UI

### Password Security
Passwords are now:
- ✅ Hashed with PBKDF2-SHA256 (Django default)
- ✅ Never sent back to frontend (even in responses)
- ✅ Verified server-side during login
- ✅ Stored securely in PostgreSQL

### CORS & Credentials
Frontend fetch calls include:
```javascript
credentials: 'include'  // Send and receive cookies
```

Backend allows credentials:
```python
CORS_ALLOW_CREDENTIALS = True
```

This enables session-based authentication across domains.

## API Endpoints Reference

### Register
```
POST /api/auth/users/register/
{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "password123",
  "password_confirm": "password123"
}
```

### Login
```
POST /api/auth/users/login/
{
  "email": "john@example.com",
  "password": "password123"
}
```

### Logout
```
POST /api/auth/users/logout/
(no body required)
```

### Current User
```
GET /api/auth/users/me/
(requires valid session)
```

## Troubleshooting

### Registration fails with "duplicate key value"
- Email already exists in database
- Use different email or check PostgreSQL users table

### Login fails with "No account found"
- Email doesn't exist in database
- Check `SELECT email FROM users;` in psql

### Login fails with "Incorrect password"
- Wrong password (obvious!)
- Passwords are case-sensitive
- No trailing spaces

### Session not persisting
- Check browser DevTools → Application → Cookies
- Look for `sessionid` cookie from localhost:8000
- Ensure CORS settings allow credentials

### CORS errors in browser console
- Check CORS_ALLOWED_ORIGINS in backend/pie_global/settings.py
- Should include `http://localhost:3000` and `http://localhost:5173`
- Restart server after changing settings

## Database Verification

```sql
-- Check all users
SELECT * FROM users;

-- Check specific user
SELECT * FROM users WHERE email = 'john@example.com';

-- Check user count
SELECT COUNT(*) FROM users;

-- Check password is hashed (not plaintext)
SELECT email, LEFT(password, 20) AS password_hash_start FROM users;
-- Should start with 'pbkdf2_sha256$'
```

## Next Steps

1. **Test Full Flow**: Register → Login → Logout → Try Login Again
2. **Check Admin**: Visit `/admin/` and manage users there
3. **Verify Passwords**: Confirm they're hashed in database (not plaintext)
4. **Test CORS**: Verify session works across origins
5. **Production Setup**: Configure environment variables for Vercel/Render

## Files to Know

- Backend app: `backend/apps/users/`
- Frontend pages: `frontend/src/pages/RegisterPage.tsx`, `LoginPage.tsx`
- API service: `frontend/src/services/api.ts`
- Test HTML: `auth-test.html`
- Documentation: `USER_AUTH_IMPLEMENTATION.md`

---

**Status**: ✅ Full server-side authentication with PostgreSQL persistence
**Accounts visible in PostgreSQL**: Yes! Your accounts are now in the database.
