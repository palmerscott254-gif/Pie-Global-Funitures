# Quick Test: Messages 403 Fix Verification

## Local Testing (Before Pushing to Render)

### Start Django Dev Server
```bash
cd backend
python manage.py runserver
```

### Test 1: List Messages (Public)
```bash
curl -X GET http://localhost:8000/api/messages/ \
  -H "Content-Type: application/json"
```

**Expected Response:**
```json
{
  "count": 0,
  "next": null,
  "previous": null,
  "results": []
}
```
✅ Status: 200 OK (no 403 error)

---

### Test 2: Create a Test Message
```bash
curl -X POST http://localhost:8000/api/messages/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test User",
    "email": "test@example.com",
    "phone": "555-0123",
    "message": "Test message for furniture inquiry"
  }'
```

**Expected Response:**
```json
{
  "success": true,
  "message": "Thank you! We will get back to you soon.",
  "id": 1
}
```
✅ Status: 201 Created

---

### Test 3: List Messages Again (Should Have One Now)
```bash
curl -X GET http://localhost:8000/api/messages/ \
  -H "Content-Type: application/json"
```

**Expected Response:**
```json
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "Test User",
      "email": "test@example.com",
      "phone": "555-0123",
      "message": "Test message for furniture inquiry",
      "status": "new",
      "reply_text": null,
      "created_at": "2026-01-07T...",
      "updated_at": "2026-01-07T..."
    }
  ]
}
```
✅ Status: 200 OK

---

### Test 4: Retrieve Single Message (Public)
```bash
curl -X GET http://localhost:8000/api/messages/1/ \
  -H "Content-Type: application/json"
```

**Expected Response:**
```json
{
  "id": 1,
  "name": "Test User",
  "email": "test@example.com",
  ...
}
```
✅ Status: 200 OK

---

### Test 5: Admin Reply (Should Still Be Protected)
```bash
curl -X POST http://localhost:8000/api/messages/1/reply/ \
  -H "Content-Type: application/json" \
  -d '{"reply_text": "Thank you for your interest"}'
```

**Expected Response:**
```json
{
  "detail": "Authentication credentials were not provided."
}
```
✅ Status: 403 Forbidden (CORRECT - admin action protected)

---

### Test 6: Rate Limiting Check (5 messages per hour per IP)
```bash
# Send 6 messages in quick succession
for i in {1..6}; do
  curl -X POST http://localhost:8000/api/messages/ \
    -H "Content-Type: application/json" \
    -d "{\"name\": \"User$i\", \"email\": \"user$i@example.com\", \"phone\": \"555-000$i\", \"message\": \"Message $i\"}"
  echo "\n"
done
```

**Expected:**
- First 5: 201 Created ✅
- 6th: 429 Too Many Requests ✅

---

## Production Testing (After Deploying to Render)

### Test 1: List Messages from Production
```bash
curl -X GET https://pie-global-funitures.onrender.com/api/messages/ \
  -H "Content-Type: application/json"
```

✅ Status: 200 OK (not 403)

---

### Test 2: Browser Test (From Vercel Frontend)

1. Open Vercel production site: `https://pie-global-funitures.vercel.app`
2. Navigate to Contact/Messages page
3. Open DevTools > Network tab
4. Trigger a fetch to list messages (if your UI has it)
5. Check the request:
   - ✅ URL: `https://pie-global-funitures.onrender.com/api/messages/`
   - ✅ Status: 200 (not 403)
   - ✅ Response: JSON array with messages

---

### Test 3: Submit a Contact Form

1. On Vercel frontend, fill out contact form
2. Click Submit
3. Check Network tab for POST request
4. **Expected:** 201 Created, success message displayed

---

## Troubleshooting

### Still Getting 403?

**Step 1:** Verify the code change was applied
```bash
grep -n "AllowAny" backend/apps/messages/views.py
```
Should show import on line ~3 and usage in `get_permissions()` method.

**Step 2:** Clear Django cache
```bash
python manage.py shell
from django.core.cache import cache
cache.clear()
exit()
```

**Step 3:** Restart dev server
```bash
# Stop current server (Ctrl+C)
python manage.py runserver
```

**Step 4:** Check for other permission classes in views

Look for `permission_classes` attribute in the viewset:
```python
# This would override get_permissions() - should NOT exist
class UserMessageViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminUser]  # ← REMOVE if present
```

---

## Deployment Checklist

- [ ] **Local tests pass** (all tests above return expected status)
- [ ] **Code changes saved** to `backend/apps/messages/views.py`
- [ ] **Git commit:** `git add backend/apps/messages/views.py && git commit -m "Fix: Allow public access to messages list/retrieve"`
- [ ] **Push to Render:** `git push origin main`
- [ ] **Wait for Render deploy** (check Render dashboard logs)
- [ ] **Production tests pass** (curl to onrender.com domain)
- [ ] **Vercel frontend test** (contact form works without 403 errors)
- [ ] **Monitor Render logs** for any errors:
  ```
  # Render Dashboard > Logs, search for:
  - ERROR
  - 403
  - "Authentication credentials"
  ```

---

## Expected Behavior Summary

| Scenario | Before Fix | After Fix |
|----------|-----------|-----------|
| **Frontend lists messages** | ❌ 403 Forbidden | ✅ 200 OK |
| **Frontend submits form** | ✅ 201 Created | ✅ 201 Created |
| **Admin replies (no auth)** | ❌ 403 Forbidden | ❌ 403 Forbidden ✓ |
| **Admin replies (with auth)** | ✅ 200 OK | ✅ 200 OK |

---

**Status:** Ready to Test  
**Estimated Time:** 5 minutes (local) + 2-5 minutes (Render deploy)
