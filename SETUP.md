# Setup & Integration Guide - SkillStalker

## ✅ Backend Endpoints

All authentication and user management endpoints are fully implemented and connected to Supabase:

### Authentication Endpoints
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login and get JWT token
- `GET /api/auth/me` - Get current logged-in user profile
- `POST /api/auth/change-password` - Change password

### User Progress Endpoints
- `PUT /api/user/progress` - Save user progress (streaks, schedule, calendar)
- `GET /api/user/progress` - Retrieve user progress

### Admin Endpoints
- `GET /api/users` - List all users (admin only)
- `DELETE /api/users/{user_id}` - Delete user (admin only)
- `POST /api/admin/test-user` - Create test user (admin only)
- `DELETE /api/admin/users/clear` - Clear all non-admin users (admin only)

## 🗄️ Database Schema

**Users Table Columns:**
- `id`: int (PRIMARY KEY)
- `fullname`: str
- `username`: str (UNIQUE)
- `email`: str (UNIQUE)
- `password_hash`: str
- `is_admin`: bool
- `profile_data`: jsonb (stores aiStudySchedule, streakDays, calendarTopics)

**Current Users in Database:**
```
👤 aruvajaswan (jaswan) - aruvajaswan@gmail.com
👤 sandy (Test User) - sabavathsandeep1621@gmail.com
```

## 🔐 Environment Configuration

The `.env` file includes:
- `SUPABASE_URL` - Supabase API endpoint
- `SUPABASE_ANON_KEY` - Supabase anon key for client operations
- `SECRET_KEY` - JWT signing key
- `FRONTEND_ORIGINS` - Allowed CORS origins
- `DIRECT_URL` - Direct PostgreSQL connection (optional)
- `DATABASE_URL` - Standard Supabase connection

## 🚀 Running the Backend

```powershell
# Activate venv
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r backend\requirements.txt

# Start backend
cd backend
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

Backend will be available at: `http://127.0.0.1:8000`

## 🎨 Frontend Pages

All pages are connected to the backend API:

### Portal Page (`portal.html`)
- **Login Form** - Username/password login
- **Register Form** - Create new account
- **Change Password Form** - Update password
- **Admin Panel** - User management (for admins only)
- **Status:** ✅ Rich UI with glassmorphism, gradients, animations

### Dashboard Page (`demo.html`)
- **Streaks Tracker** - 30-day progress tracker
- **Calendar** - Edit topics by date
- **Study Planner** - Generate study schedule
- **Auth Sync** - Auto-syncs progress to backend
- **Status:** ✅ Connected with auth-sync.js

### Practice Page (`practice.html`)
- **Language Selection** - HTML, CSS, JS, Python
- **Practice Prompts** - Auto-generated challenges
- **Code Editor** - Run JavaScript/HTML code
- **Auth Protection** - Requires valid JWT
- **Status:** ✅ Connected with auth-sync.js

### Coding Page (`coding.html`)
- **Video Links** - Language tutorials
- **Status:** ✅ Ready to use

## 📋 Test Credentials

**Regular User:**
- Username: `sandy`
- Password: `2026`

**Admin User:**
- Username: `skillstalkeradmin`
- Password: `727303949`

## 🔄 Frontend-Backend Flow

1. User logs in via `portal.html` form
2. Frontend calls `POST /api/auth/login`
3. Backend returns JWT token
4. Frontend stores token in `localStorage.ss_token`
5. Dashboard pages load with `auth-sync.js`
6. Auth checks JWT validity, redirects if expired
7. Progress data syncs automatically on page load
8. Changes (streaks, schedule, calendar) auto-sync to backend

## ✨ Features Implemented

### Security
- JWT-based authentication
- Bcrypt password hashing
- CORS restricted to allowed origins
- Admin-only endpoints with role checking
- Token expiration (7 days)

### User Progress Tracking
- 30-day streak counter
- Study schedule generator
- Topic scheduling by calendar date
- Multi-device persistence (via profile_data)

### Admin Features
- User listing and management
- User deletion
- Test user creation
- Bulk user clearing

## 🧪 Testing the API

Use curl or Postman:

```bash
# Register
curl -X POST http://127.0.0.1:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"fullname":"Test","username":"testuser","email":"test@example.com","password":"password123"}'

# Login
curl -X POST http://127.0.0.1:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"password123"}'

# Get profile (replace TOKEN)
curl -X GET http://127.0.0.1:8000/api/auth/me \
  -H "Authorization: Bearer TOKEN"

# Save progress
curl -X PUT http://127.0.0.1:8000/api/user/progress \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"profile_data":{"aiStudySchedule":[],"streakDays":{"1":"completed"},"calendarTopics":{}}}'
```

## 📝 Notes

- Passwords must be at least 6 characters
- Username must be unique
- Email must be unique
- Admin username is hardcoded as "skillstalkeradmin"
- Profile data is stored as JSON in database
- All endpoints require HTTPS in production (currently HTTP for local dev)

## 🔗 Quick Links

- **Portal:** http://127.0.0.1:5500/frontend/portal.html
- **Dashboard:** http://127.0.0.1:5500/frontend/demo.html
- **Backend API:** http://127.0.0.1:8000
- **API Docs:** http://127.0.0.1:8000/docs
- **Supabase Project:** https://app.supabase.co

---

**Status:** ✅ All systems operational and fully integrated
