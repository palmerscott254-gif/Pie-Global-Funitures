# User Authentication System Implementation

## Overview
Migrated from client-side localStorage authentication to a full server-side authentication system with PostgreSQL persistence.

## What Changed

### Backend (Django)
Created a complete `apps/users` authentication app with:

#### Models (`backend/apps/users/models.py`)
- **User Model**: Custom user model with UUID primary key
  - `name`: User's full name
  - `email`: Unique email address (indexed for fast lookups)
  - `password`: Hashed password using Django's PBKDF2-SHA256
  - `created_at`, `updated_at`: Timestamps
  - `is_active`: User status flag
  - Custom methods:
    - `set_password()`: Hash and store password securely
    - `check_password()`: Verify password during login
    - `save()`: Auto-hash passwords on save

#### Serializers (`backend/apps/users/serializers.py`)
- `UserRegisterSerializer`: Validates registration data, confirms password match
- `UserLoginSerializer`: Validates login credentials
- `UserSerializer`: Returns safe user data (no password)

#### Views (`backend/apps/users/views.py`)
- **UserViewSet** with custom actions:
  - `POST /api/auth/users/register/`: Create new account
    - Validates email uniqueness
    - Hashes password with PBKDF2-SHA256
    - Creates Django session
    - Returns user data
  - `POST /api/auth/users/login/`: Authenticate user
    - Verifies email exists
    - Checks password hash
    - Creates session on success
    - Returns user data
  - `POST /api/auth/users/logout/`: Destroy session
  - `GET /api/auth/users/me/`: Get current authenticated user from session

#### Database
- New `users` table in PostgreSQL with proper indexing on email
- Migration applied: `apps/users/migrations/0001_initial.py`

#### Admin
- User management in Django admin (`/admin/`)
- Can view, filter, and manage users

### Frontend (React)

#### RegisterPage (`frontend/src/pages/RegisterPage.tsx`)
**Before**: Stored accounts in `localStorage` with plaintext passwords
```typescript
const newUsers = [...existingUsers, { name, email, password }];
localStorage.setItem('pgf-auth-users', JSON.stringify(newUsers));
```

**After**: Calls backend API
```typescript
const response = await fetch(`${API_URL}/auth/users/register/`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  credentials: 'include', // Send/receive session cookies
  body: JSON.stringify({
    name,
    email,
    password,
    password_confirm: passwordConfirm,
  }),
});
```

**Changes**:
- Added password confirmation field
- Backend validates passwords match
- Backend returns user ID and other metadata
- Session cookie automatically set for auth

#### LoginPage (`frontend/src/pages/LoginPage.tsx`)
**Before**: Compared plaintext passwords in localStorage
```typescript
const user = existingUsers.find((u) => u.email.toLowerCase() === email.toLowerCase());
if (user.password !== password) { // Plaintext comparison!
  toast.error('Incorrect password.');
}
```

**After**: Calls backend for secure verification
```typescript
const response = await fetch(`${API_URL}/auth/users/login/`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  credentials: 'include', // Session cookie authentication
  body: JSON.stringify({ email, password }),
});
```

**Changes**:
- Removed email suggestions (no longer needed - backend validates)
- Removed localStorage registry lookup
- Backend handles password verification
- Session cookie provides stateful authentication

#### API Service (`frontend/src/services/api.ts`)
- Added `API_URL` export for auth components
- `API_URL` removes `/api/` suffix to allow auth endpoints at `/api/auth/`
- Maintains full axios instance for other API calls

### Session-Based Authentication
- Django session stored in database (not cookies-only)
- Session created when user registers or logs in
- `credentials: 'include'` in fetch requests ensures cookies are sent/received
- Session timeout: 86400 seconds (1 day)
- CORS configured to allow credentials
- CSRF protection enabled for production

## Security Improvements

| Aspect | Before | After |
|--------|--------|-------|
| Password storage | Plaintext in localStorage | PBKDF2-SHA256 hashed in PostgreSQL |
| Transport | No encryption in dev | HTTPS in production |
| Session management | Browser localStorage | Secure HTTP-only server session |
| Data persistence | Deleted on browser clear | Permanent PostgreSQL storage |
| Email uniqueness | Client-side check only | Database constraint (unique index) |
| Authentication | Client-side logic | Server-side validation |

## API Endpoints

### Register
```
POST /api/auth/users/register/
Content-Type: application/json

{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "securepassword",
  "password_confirm": "securepassword"
}

Response (201 Created):
{
  "success": true,
  "message": "Account created successfully.",
  "user": {
    "id": "uuid-string",
    "name": "John Doe",
    "email": "john@example.com",
    "created_at": "2026-01-07T14:00:00Z"
  }
}
```

### Login
```
POST /api/auth/users/login/
Content-Type: application/json
Cookie: sessionid=abc123...

{
  "email": "john@example.com",
  "password": "securepassword"
}

Response (200 OK):
{
  "success": true,
  "message": "Signed in successfully.",
  "user": {
    "id": "uuid-string",
    "name": "John Doe",
    "email": "john@example.com",
    "created_at": "2026-01-07T14:00:00Z"
  }
}
```

### Logout
```
POST /api/auth/users/logout/

Response (200 OK):
{
  "success": true,
  "message": "Logged out successfully."
}
```

### Get Current User
```
GET /api/auth/users/me/
Cookie: sessionid=abc123...

Response (200 OK):
{
  "success": true,
  "user": {
    "id": "uuid-string",
    "name": "John Doe",
    "email": "john@example.com",
    "created_at": "2026-01-07T14:00:00Z"
  }
}

Response (401 Unauthorized):
{
  "success": false,
  "error": "Not authenticated."
}
```

## Testing

### Using the Test HTML Page
Open `auth-test.html` in your browser and test:
1. **Register**: Create new account
2. **Login**: Sign in with registered email
3. **Get Current User**: Verify authenticated session
4. **Logout**: Destroy session

### Using cURL
```bash
# Register
curl -X POST http://localhost:8000/api/auth/users/register/ \
  -H "Content-Type: application/json" \
  -d '{"name":"Test User","email":"test@example.com","password":"testpass123","password_confirm":"testpass123"}'

# Login
curl -X POST http://localhost:8000/api/auth/users/login/ \
  -H "Content-Type: application/json" \
  -c cookies.txt \
  -d '{"email":"test@example.com","password":"testpass123"}'

# Get current user (using cookies from login)
curl -X GET http://localhost:8000/api/auth/users/me/ \
  -b cookies.txt
```

### Using Frontend
1. Navigate to `/register` - Create account
2. Navigate to `/login` - Sign in
3. Accounts now stored in PostgreSQL
4. Check admin `/admin/` - Verify users in database

## Database Schema

```sql
CREATE TABLE users (
  id UUID PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  email VARCHAR(254) NOT NULL UNIQUE,
  password VARCHAR(255) NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE AUTO_NOW_ADD,
  updated_at TIMESTAMP WITH TIME ZONE AUTO_NOW,
  is_active BOOLEAN DEFAULT TRUE
);

CREATE INDEX idx_users_email ON users(email);
```

## Configuration Required

### Backend (`backend/.env`)
Already configured in `settings.py`:
- `SESSION_ENGINE`: Database-backed sessions
- `CORS_ALLOW_CREDENTIALS`: True (required for sessions)
- `CSRF_TRUSTED_ORIGINS`: Includes frontend domains

### Frontend (`frontend/.env`)
Example:
```
VITE_API_URL=http://localhost:8000/api/
```

Or set via environment:
- Vercel: Project Settings → Environment Variables
- Local: Create `.env` file in frontend directory

## Migration Notes

### Old Data Migration (Optional)
If you need to migrate existing localStorage accounts to PostgreSQL:

```python
# In backend shell or management command
import json
from apps.users.models import User

# Get users from frontend localStorage export
users_data = [
  {"name": "...", "email": "...", "password": "..."},
  # ...
]

for user_data in users_data:
  User.objects.create(
    name=user_data['name'],
    email=user_data['email'],
    password=user_data['password']  # Will auto-hash in save()
  )
```

## File Structure
```
backend/
├── apps/
│   └── users/
│       ├── migrations/
│       │   ├── __init__.py
│       │   └── 0001_initial.py
│       ├── admin.py          # Django admin configuration
│       ├── apps.py           # App config
│       ├── models.py         # User model
│       ├── serializers.py    # DRF serializers
│       ├── urls.py           # API endpoints
│       ├── views.py          # ViewSet and actions
│       └── __init__.py
│
├── pie_global/
│   ├── settings.py           # Updated with users app
│   └── urls.py               # Updated with auth routes
│
frontend/
├── src/
│   ├── pages/
│   │   ├── RegisterPage.tsx  # Updated - calls API
│   │   └── LoginPage.tsx     # Updated - calls API
│   └── services/
│       └── api.ts            # Updated - exports API_URL
```

## Troubleshooting

### "No account found for this email"
- Ensure user was created via registration endpoint
- Check `users` table in PostgreSQL database

### "Incorrect password"
- Passwords are hashed - visual comparison won't work
- Use login endpoint or admin to test

### Session not persisting
- Ensure `credentials: 'include'` is set in fetch calls
- Check browser DevTools → Application → Cookies for `sessionid`
- Verify `CORS_ALLOW_CREDENTIALS = True` in settings.py

### CORS errors
- Check `CORS_ALLOWED_ORIGINS` in settings.py
- Include frontend domain for production
- `CORS_ALLOW_CREDENTIALS` must be True

### Database connection errors
- Ensure PostgreSQL is running
- Check `DATABASE_URL` or individual postgres settings
- Run `python manage.py check` to verify config

## Next Steps

1. **Email Verification**: Add email confirmation on registration
2. **Password Reset**: Implement forgot password flow
3. **JWT Tokens**: Switch from session-based to token-based auth
4. **Social Login**: Add OAuth2 (Google, GitHub, etc.)
5. **Two-Factor Auth**: Add 2FA for security
6. **User Profiles**: Extend User model with bio, avatar, etc.

## Summary

✅ Accounts now stored in PostgreSQL (not localStorage)
✅ Passwords securely hashed with PBKDF2-SHA256
✅ Session-based authentication with secure cookies
✅ Full API endpoints for register/login/logout
✅ CORS and CSRF protection enabled
✅ Admin management interface available
✅ Ready for production deployment

Your accounts can now be seen in PostgreSQL! 🎉
