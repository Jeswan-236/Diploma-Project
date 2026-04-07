# API Integration & Troubleshooting Guide

## ✅ Verified Connections

### Frontend ↔ Backend API Mapping

| Frontend Form | Backend Endpoint | Method | Status |
|---|---|---|---|
| Login Form (portal.html) | `/api/auth/login` | POST | ✅ Connected |
| Register Form (portal.html) | `/api/auth/register` | POST | ✅ Connected |
| Get Profile (after login) | `/api/auth/me` | GET | ✅ Connected |
| Change Password Form | `/api/auth/change-password` | POST | ✅ Connected |
| Admin User Listing | `/api/users` | GET | ✅ Connected |
| Dashboard Progress Sync | `/api/user/progress` | PUT/GET | ✅ Connected |

## 🔄 Current Data Flow

### Login Flow
1. User enters credentials in `portal.html` login form
2. Frontend calls `POST /api/auth/login` with username & password
3. Backend verifies credentials against Supabase users table
4. Backend returns JWT token
5. Frontend stores in `localStorage.ss_token`
6. Frontend calls `GET /api/auth/me` to get user profile
7. User redirected to `demo.html` dashboard

### Progress Sync Flow
1. User makes changes (mark streak, edit schedule, add topics)
2. `demo3.js` saves changes to localStorage
3. `demo3.js` calls `syncDataWithServer()` from `auth-sync.js`
4. Frontend `PUT /api/user/progress` sends data to backend
5. Backend updates `profile_data` column in Supabase
6. On next page load, `GET /api/user/progress` retrieves saved data

## 🗄️ Sample API Responses

### Login Response
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### User Profile Response
```json
{
  "id": 1,
  "fullname": "John Doe",
  "username": "johndoe",
  "email": "john@example.com",
  "is_admin": false
}
```

### Progress Response
```json
{
  "profile_data": {
    "aiStudySchedule": [...],
    "streakDays": {"1": "completed", "2": "completed"},
    "calendarTopics": {"0-1": {"subject": "HTML", "topic": "basics", "time": "morning"}}
  }
}
```

## 🔐 JWT Token Handling

- Token stored in: `localStorage.ss_token`
- Token format: `Bearer <token>`
- Token expiration: 7 days
- Used in header: `Authorization: Bearer <token>`
- Retrieved by: All `apiRequest()` calls in portal.html

## ⚠️ Common Issues & Solutions

### Issue: "CORS blocked" error
**Solution:** Ensure `FRONTEND_ORIGINS` in `.env` includes your dev URL
```
FRONTEND_ORIGINS=http://127.0.0.1:5500,http://localhost:5500,http://local host:8000
```

### Issue: "Invalid credentials" on login
**Solution:** 
- Username and password are case-sensitive
- Check user exists: run `check_db.py`
- Test credentials: `sandy` / `2026`

### Issue: "Token expired" redirect to portal
**Solution:** This is expected after 7 days. User needs to login again.
To extend token lifetime, change `ACCESS_TOKEN_EXPIRE_MINUTES` in `main.py`:
```python
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 30  # 30 days
```

### Issue: Progress not saving
**Solution:**
- Open browser DevTools (F12)
- Check Network tab for `PUT /api/user/progress` request
- Verify token is sent: should see `Authorization: Bearer ...` header
- Check response for errors

### Issue: Admin Panel not showing
**Solution:**
- Login with admin account: `skillstalkeradmin` / `727303949`
- Check browser console for errors
- Verify `is_admin` is `true` in database (may be NULL initially)

## 📊 Database Health Check

Run the diagnostics script:
```powershell
cd e:\Diploma-Project
.\venv\Scripts\Activate.ps1
cd backend
python check_db.py
```

Expected output shows:
- Total users
- Users table columns
- Current user records
- Profile data status

## 🧪 Manual API Testing

### Via Browser Console
```javascript
// Test login
fetch('http://127.0.0.1:8000/api/auth/login', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({username: 'sandy', password: '2026'})
})
.then(r => r.json())
.then(d => console.log(d))

// Get token
const token = localStorage.getItem('ss_token')
console.log(token)

// Check profile with token
fetch('http://127.0.0.1:8000/api/auth/me', {
  headers: {'Authorization': `Bearer ${token}`}
})
.then(r => r.json())
.then(d => console.log(d))
```

### Via Curl/PowerShell
```powershell
# Login
$response = curl -Method Post `
  -Uri "http://127.0.0.1:8000/api/auth/login" `
  -ContentType "application/json" `
  -Body (@{username="sandy"; password="2026"} | ConvertTo-Json)

$token = ($response | ConvertFrom-Json).access_token
Write-Host "Token: $token"

# Get profile
curl -Uri "http://127.0.0.1:8000/api/auth/me" `
  -Headers @{Authorization="Bearer $token"}
```

## 📝 Notes for Production

⚠️ Before deploying to production:

1. **HTTPS only** - Change all `http://` to `https://`
2. **Environment variables** - Never commit `.env` file
3. **CORS origins** - Restrict to your actual domain, not `["*"]`
4. **Token expiration** - Consider shorter expiration for security
5. **Password requirements** - Add minimum complexity rules
6. **Rate limiting** - Add API rate limiting
7. **Logging** - Add request/error logging
8. **Database backups** - Set up automated Supabase backups
9. **API documentation** - Generate from FastAPI auto-docs at `/docs`
10. **Testing** - Create comprehensive test suite

## 📚 Reference

- FastAPI Docs: http://127.0.0.1:8000/docs
- Supabase Docs: https://supabase.com/docs
- JWT Info: https://jwt.io
- CORS Info: https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS

---

**Last Updated:** April 7, 2026
**System Status:** ✅ All endpoints operational and tested
