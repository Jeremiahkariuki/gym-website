#!/usr/bin/env python
"""
Quick Start Guide for Gym Management System
"""

# STEP 1: Start the Development Server
# =====================================
# Open PowerShell and run:
# cd c:\Users\Administrator\Desktop\gym
# env\Scripts\activate
# python manage.py runserver

# STEP 2: Access the Application
# ==============================
# Web Interface: http://localhost:8000
# Admin Panel: http://localhost:8000/admin
# Login Page: http://localhost:8000/login

# STEP 3: Create Admin Account (if not exists)
# ============================================
# python manage.py createsuperuser
# Then follow prompts to create username and password

# DEFAULT LOGIN CREDENTIALS (After Creating Superuser)
# ===================================================
# Username: (as you set during createsuperuser)
# Password: (as you set during createsuperuser)

# MAIN PAGES AND URLS
# ===================

"""
DASHBOARD & OVERVIEW
- URL: http://localhost:8000/dashboard/
- Features: Key metrics, quick actions, reports

MEMBERS
- List: http://localhost:8000/members/
- Add New: http://localhost:8000/members/new/
- Edit: http://localhost:8000/members/<id>/edit/
- Delete: http://localhost:8000/members/<id>/delete/
- Profile: http://localhost:8000/members/<id>/

MEMBERSHIP PLANS
- List: http://localhost:8000/plans/
- Add New: http://localhost:8000/plans/new/

MEMBERSHIP ASSIGNMENT
- Assign: http://localhost:8000/members/<id>/membership/

PAYMENTS
- Record: http://localhost:8000/members/<id>/payment/
- Report: http://localhost:8000/revenue-report/

ATTENDANCE
- Check-in: http://localhost:8000/present/<id>/
- Report: http://localhost:8000/attendance-report/

AUTHENTICATION
- Login: http://localhost:8000/login/
- Logout: http://localhost:8000/logout/

ADMIN
- Admin Panel: http://localhost:8000/admin/
"""

# COMMON WORKFLOW
# ===============

"""
1. CREATE MEMBERSHIP PLANS
   a. Login to http://localhost:8000/login/
   b. Go to Plans → + Add Plan
   c. Fill in: Name (e.g., "Monthly"), Price, Duration in Days
   d. Click "Add Plan"

2. ADD MEMBERS
   a. Go to Members → + Add Member
   b. Fill in: Full Name, Phone (unique), Email (optional), Address (optional)
   c. Click "Add Member"

3. ASSIGN MEMBERSHIPS
   a. Go to Members → Select a member
   b. Click "Assign Membership"
   c. Choose plan and start date
   d. Click "Assign Membership"

4. RECORD PAYMENTS
   a. Go to Members → Select a member
   b. Click "Record Payment"
   c. Enter: Amount, Payment Method (Cash/M-Pesa/Bank), Reference (optional)
   d. Click "Record Payment"

5. CHECK-IN MEMBERS
   a. Go to Dashboard or Members page
   b. Click "✓ Check In" next to member name
   c. Member is marked present for today

6. VIEW REPORTS
   a. Dashboard → 👥 Attendance Report (top members)
   b. Dashboard → 💰 Revenue Report (payment statistics)
"""

# DATABASE OPERATIONS
# ===================

"""
Run migrations (if you modified models):
    python manage.py makemigrations
    python manage.py migrate

View database with Django shell:
    python manage.py shell
    >>> from base.gym.models import Member
    >>> Member.objects.all()

Create superuser:
    python manage.py createsuperuser

Load sample data:
    python manage.py loaddata (if fixtures exist)
"""

# TROUBLESHOOTING
# ===============

"""
Issue: Port 8000 already in use
Solution: python manage.py runserver 8001

Issue: Database locked
Solution: Delete db.sqlite3 and run:
    python manage.py migrate

Issue: Static files not loading
Solution: python manage.py collectstatic

Issue: Module not found
Solution: pip install -r requirements.txt

Issue: Templates not found
Solution: Check TEMPLATES setting in gym/settings.py
"""

# PROJECT STRUCTURE
# =================

"""
gym/ (Main Project Directory)
├── manage.py (Django command-line tool)
├── db.sqlite3 (Database file)
├── README.md (Project documentation)
├── IMPLEMENTATION_SUMMARY.md (What was implemented)
│
├── gym/ (Main project settings)
│   ├── settings.py (Configuration)
│   ├── urls.py (Main URL routing)
│   ├── asgi.py (ASGI config)
│   └── wsgi.py (WSGI config)
│
├── base/gym/ (Main app)
│   ├── models.py (Database models)
│   ├── views.py (View functions)
│   ├── urls.py (App URL routing)
│   ├── forms.py (Django forms)
│   ├── admin.py (Admin configuration)
│   ├── apps.py
│   ├── tests.py
│   ├── migrations/ (Database migrations)
│   └── templates/gym/ (HTML templates)
│
└── env/ (Virtual environment)
"""

# KEY MODELS
# ==========

"""
Member
- full_name (CharField)
- phone (CharField, unique)
- email (EmailField, optional)
- address (CharField, optional)
- joined_on (DateField, auto)
- membership_Plan (ForeignKey to MembershipPlan)

MembershipPlan
- name (CharField)
- price (DecimalField)
- duration_days (PositiveIntegerField)

Membership
- member (ForeignKey to Member)
- plan (ForeignKey to MembershipPlan)
- start_date (DateField)
- end_date (DateField, auto-calculated)
- is_active (BooleanField)

Payment
- member (ForeignKey to Member)
- Membership (ForeignKey to Membership, optional)
- amount (DecimalField)
- paid_on (DateTimeField)
- method (CharField: Cash/M-Pesa/Bank)
- reference (CharField, optional)
- date (DateField)

Attendance
- member (ForeignKey to Member)
- date (DateTimeField)
- unique_together: (member, date)
"""

# USEFUL COMMANDS
# ===============

# Start development server
# python manage.py runserver

# Run migrations
# python manage.py migrate

# Make migrations (after model changes)
# python manage.py makemigrations

# Open Django shell
# python manage.py shell

# Create superuser
# python manage.py createsuperuser

# Collect static files
# python manage.py collectstatic

# Run tests
# python manage.py test

# Check project status
# python manage.py check

print("""
╔═══════════════════════════════════════════════════════════════╗
║   🏋️  GYM MANAGEMENT SYSTEM - QUICK START GUIDE              ║
║                                                               ║
║  Status: ✅ READY TO USE                                    ║
║                                                               ║
║  To Start:                                                    ║
║  1. cd c:\\Users\\Administrator\\Desktop\\gym              ║
║  2. env\\Scripts\\activate                                   ║
║  3. python manage.py runserver                               ║
║  4. Visit: http://localhost:8000/login/                      ║
║                                                               ║
║  Default Admin: Create with 'createsuperuser' command        ║
║                                                               ║
║  Features Included:                                          ║
║  ✓ Member Management (CRUD)                                 ║
║  ✓ Membership Plans                                          ║
║  ✓ Attendance Tracking                                       ║
║  ✓ Payment Recording                                         ║
║  ✓ Attendance Reports                                        ║
║  ✓ Revenue Reports                                           ║
║  ✓ Professional UI/Dashboard                                 ║
║  ✓ Admin Panel                                               ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
""")
