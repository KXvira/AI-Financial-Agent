# Admin Panel - Quick Reference Guide

## 🚀 Quick Start

### Starting the Application
```bash
# 1. Start Backend (Terminal 1)
cd /home/munga/Desktop/AI-Financial-Agent
/home/munga/Desktop/AI-Financial-Agent/venv-ocr/bin/python -m uvicorn backend.app:app --host 0.0.0.0 --port 8000 --reload

# 2. Start Frontend (Terminal 2)
cd /home/munga/Desktop/AI-Financial-Agent/finance-app
npm run dev
```

### Access URLs
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

### Default Admin Login
- **Email**: admin@finguard.com
- **Password**: admin123

---

## 📍 Navigation

### Admin Pages
1. **Dashboard**: `/admin` or `/admin/page.tsx`
   - View system stats
   - Quick actions
   - Permission overview

2. **User Management**: `/admin/users`
   - List all users
   - Create/Edit/Delete users
   - Search and filter

3. **Activity Logs**: `/admin/activity`
   - View audit logs
   - Filter by action/status
   - Search by email/IP

---

## 🔑 User Roles & Permissions

### Role Hierarchy
```
ADMIN (*)          → Full system access
OWNER (*)          → Full system access (equal to ADMIN)
MANAGER (18)       → User & data management
ACCOUNTANT (14)    → Financial records
VIEWER (6)         → Read-only access
```

### Permission Examples
- **ADMIN/OWNER**: ["*"] - All permissions
- **MANAGER**: ["users.view", "users.create", "users.update", ...]
- **ACCOUNTANT**: ["invoices.create", "invoices.view", ...]
- **VIEWER**: ["dashboard.view", "invoices.view", ...]

---

## 🛠️ API Endpoints

### Authentication
```bash
# Login
POST /api/auth/login
Body: {"email": "...", "password": "..."}

# Register
POST /api/auth/register
Body: {user details}
```

### User Management
```bash
# List users
GET /admin/users?page=1&limit=10&search=query&role=admin&status=active

# Get user
GET /admin/users/{id}

# Create user
POST /admin/users
Body: {
  "email": "user@example.com",
  "password": "password123",
  "confirm_password": "password123",
  "company_name": "Company Name",
  "phone_number": "+254712345678",
  "role": "viewer"
}

# Update user
PUT /admin/users/{id}
Body: {
  "company_name": "New Name",
  "phone_number": "+254798765432",
  "role": "manager",
  "status": "active"
}

# Delete user (soft delete)
DELETE /admin/users/{id}
```

### Admin Operations
```bash
# Get stats
GET /admin/stats

# Get activity logs
GET /admin/activity?page=1&limit=20&action=login&success=true

# Get permissions
GET /admin/permissions

# Reset password
POST /admin/users/{id}/reset-password
Body: {"new_password": "..."}
```

---

## 📋 Common Tasks

### Creating a New User
1. Navigate to `/admin/users`
2. Click "Add User" button
3. Fill in form:
   - Email: Must be unique, valid format
   - Password: Min 8 characters
   - Confirm Password: Must match
   - Company: Min 2 characters
   - Phone: Format +254XXXXXXXXX
   - Role: Select from dropdown
4. Click "Create User"
5. User appears in list

### Editing User Details
1. Click Edit icon on user row
2. Modify fields (email cannot be changed)
3. Click "Update User"
4. Changes saved immediately

### Deleting a User
1. Click Delete icon
2. Review user details
3. Click "Delete User"
4. User marked as inactive (soft delete)

### Searching Users
1. Enter email or company name in search box
2. Press Enter or click search button
3. Results filter automatically

### Filtering Users
1. Select role from dropdown (All/Admin/Owner/Manager/Accountant/Viewer)
2. Select status from dropdown (All/Active/Inactive/Suspended/Pending)
3. Results update automatically

---

## 🔍 Activity Log Actions

### Action Types
- `login` - User logged in
- `logout` - User logged out
- `register` - New user registered
- `password_reset` - Password was reset
- `user_created` - Admin created a user
- `user_updated` - Admin updated a user
- `user_deleted` - Admin deleted a user
- `permission_denied` - Access attempt denied

### Filtering Logs
1. Search by email or IP address
2. Filter by action type
3. Filter by success/failure status
4. Navigate pages with Previous/Next

---

## 🎨 UI Components

### Stat Cards
- Display key metrics
- Icons for visual clarity
- Real-time data updates

### User Table
- Sortable columns
- Pagination controls
- Action buttons (Edit/Delete)
- Verification indicators

### Modals
- Form inputs with validation
- Loading states
- Error messages
- Success callbacks

### Toast Notifications
- Auto-dismiss after 5 seconds
- Manual close button
- Success/error styling

---

## 🐛 Troubleshooting

### Backend Not Responding
```bash
# Check if running
curl http://localhost:8000/

# Restart backend
pkill -f uvicorn
/home/munga/Desktop/AI-Financial-Agent/venv-ocr/bin/python -m uvicorn backend.app:app --reload
```

### Frontend Not Loading
```bash
# Check if running
curl http://localhost:3000/

# Restart frontend
pkill -f "next dev"
cd finance-app && npm run dev
```

### Authentication Errors
1. Check if token expired (1 hour)
2. Clear localStorage: `localStorage.clear()`
3. Log in again

### Permission Denied
1. Verify user role: Check /admin dashboard
2. Ensure role has required permission
3. Try logging in as admin

---

## 🔒 Security Notes

### Passwords
- Minimum 8 characters required
- Stored hashed with bcrypt
- Never exposed in API responses

### Tokens
- JWT with 1-hour expiry
- Stored in localStorage
- Refresh token lasts 7 days

### Permissions
- Checked on every admin endpoint
- Self-deletion prevented
- Audit logs created for accountability

---

## 📊 Validation Rules

### Email
- Format: `user@domain.com`
- Must be unique in system

### Phone Number
- Format: `+254XXXXXXXXX` (Kenya)
- Exactly 13 characters
- Must start with +254

### Password
- Minimum 8 characters
- Must match confirm password

### Company Name
- Minimum 2 characters
- Maximum 100 characters

---

## 🧪 Test Accounts

| Email | Password | Role | Permissions |
|-------|----------|------|-------------|
| admin@finguard.com | admin123 | ADMIN | All (*) |
| testowner@finguard.com | owner123 | OWNER | All (*) |
| accountant@finguard.com | accountant123 | ACCOUNTANT | 14 permissions |

---

## 📝 File Locations

### Backend
```
backend/
├── admin/
│   ├── router.py          # Admin API endpoints (494 lines)
│   └── __init__.py
├── auth/
│   ├── models.py          # User models (200 lines)
│   ├── service.py         # Auth service (597 lines)
│   └── router.py          # Auth endpoints
└── app.py                 # Main FastAPI app
```

### Frontend
```
finance-app/
├── app/
│   └── admin/
│       ├── page.tsx               # Dashboard (340 lines)
│       ├── users/
│       │   └── page.tsx           # User management (495 lines)
│       └── activity/
│           └── page.tsx           # Activity logs (376 lines)
└── components/
    ├── CreateUserModal.tsx        # Create modal (375 lines)
    ├── EditUserModal.tsx          # Edit modal (352 lines)
    └── DeleteUserModal.tsx        # Delete modal (214 lines)
```

### Documentation
```
docs/
├── ADMIN_PANEL_SUMMARY.md         # Comprehensive summary
├── CRUD_TEST_REPORT.md            # Testing report
├── USER_FORM_MODALS.md            # Modal documentation
└── ADMIN_QUICK_REFERENCE.md       # This file
```

---

## 🎯 Best Practices

### Frontend
1. Always check authentication before API calls
2. Handle loading states properly
3. Show user-friendly error messages
4. Validate inputs before submission
5. Refresh data after mutations

### Backend
1. Always validate inputs
2. Check permissions on protected endpoints
3. Log important actions
4. Return appropriate HTTP status codes
5. Never expose sensitive data

### Security
1. Use HTTPS in production
2. Rotate JWT secrets regularly
3. Implement rate limiting
4. Monitor failed login attempts
5. Regular security audits

---

## 🚨 Common Errors

### 401 Unauthorized
- **Cause**: Token expired or invalid
- **Fix**: Log in again

### 403 Forbidden
- **Cause**: Insufficient permissions
- **Fix**: Check user role, use admin account

### 422 Unprocessable Entity
- **Cause**: Validation error
- **Fix**: Check form inputs, ensure all required fields filled

### 404 Not Found
- **Cause**: User or resource doesn't exist
- **Fix**: Verify ID, refresh user list

### 500 Internal Server Error
- **Cause**: Backend error
- **Fix**: Check backend logs, restart server

---

## 📞 Quick Commands

### Check Server Status
```bash
# Backend
curl http://localhost:8000/

# Frontend
curl http://localhost:3000/

# MongoDB
mongosh "mongodb+srv://cluster0.y7595ne.mongodb.net/"
```

### View Logs
```bash
# Backend logs
tail -f /tmp/backend.log

# Frontend logs
tail -f /tmp/nextjs.log
```

### Test API
```bash
# Get token
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@finguard.com","password":"admin123"}' | jq -r '.access_token')

# Test endpoint
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/admin/stats | jq '.'
```

---

## ✅ Completion Checklist

### For Users
- [ ] Logged in successfully
- [ ] Can view dashboard
- [ ] Can create users
- [ ] Can edit users
- [ ] Can delete users
- [ ] Can view activity logs
- [ ] Understand role permissions

### For Developers
- [ ] Backend running
- [ ] Frontend running
- [ ] Database connected
- [ ] All endpoints working
- [ ] Tests passing
- [ ] Documentation complete

---

**Last Updated**: October 14, 2025  
**Version**: 1.0  
**Status**: Production Ready (Pending Phase 6)
