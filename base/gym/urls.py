from django.urls import path
from django.contrib.auth import views as auth_views
from django.views.generic import RedirectView
from . import views

urlpatterns = [
    # Root
    path("", views.home_view, name="home"),
    
    # Public Pages
    path("classes/", views.class_schedule_view, name="class_schedule"),
    path("contact/", views.contact_view, name="contact"),
    
    # Members
    path("members/", views.member_list, name="member_list"),
    path("members/<int:member_id>/", views.member_detail, name="member_detail"),
    path("members/<int:member_id>/edit/", views.member_edit, name="member_edit"),
    path("members/<int:member_id>/delete/", views.member_delete, name="member_delete"),
    
    # Authentication
    path("login/", auth_views.LoginView.as_view(template_name="gym/login.html", form_class=views.LoginForm), name="login"),
    path("register/", views.register_view, name="register"),
    path("staff/add/", views.staff_create, name="staff_create"),
    path("logout/", views.logout_view, name="logout"), 
    
    # Dashboard
    path("dashboard/", views.dashboard, name="dashboard"),
    path("dashboard-redirect/", views.login_redirect_view, name="login_redirect"),
    
    # Portal
    path("portal/", views.portal_dashboard, name="portal_dashboard"),
    path("portal/class/toggle/<int:class_id>/", views.portal_class_toggle, name="portal_class_toggle"),
    path("portal/workout/", views.portal_workout, name="portal_workout"),
    path("portal/diet/", views.portal_diet, name="portal_diet"),
    path("portal/payments/", views.portal_payments, name="portal_payments"),
    path("portal/id-card/", views.portal_id_card, name="portal_id_card"),
    path("portal/notifications/", views.portal_notifications_optin, name="portal_notifications_optin"),
    path("portal/subscribe/<int:plan_id>/", views.portal_subscribe, name="portal_subscribe"),
    path("portal/exercise-library/", views.portal_exercise_library, name="portal_exercise_library"),
    path("portal/progress-gallery/", views.portal_progress_gallery, name="portal_progress_gallery"),
    path("portal/profile-hub/", views.portal_profile_hub, name="portal_profile_hub"),
    path("portal/achievements/", views.portal_achievement_room, name="portal_achievement_room"),
    
    # Branches
    path("manage/branches/", views.branch_list, name="branch_list"),
    path("manage/branches/create/", views.branch_create, name="branch_create"),
    path("manage/branches/edit/<int:branch_id>/", views.branch_edit, name="branch_edit"),
    path("manage/branches/delete/<int:branch_id>/", views.branch_delete, name="branch_delete"),
    path("branch/set/<int:branch_id>/", views.set_active_branch, name="set_active_branch"),

    
    # Attendance
    path("present/<int:member_id>/", views.mark_present, name="mark_present"),
    path("attendance-report/", views.attendance_report, name="attendance_report"),
    
    # Plans
    path("plans/", views.plan_list, name="plan_list"),
    path("plans/new/", views.plan_create, name="plan_create"),
    path("plans/<int:pk>/edit/", views.plan_edit, name="plan_edit"),
    path("plans/<int:pk>/delete/", views.plan_delete, name="plan_delete"),
    
    # Membership
    path("members/<int:member_id>/membership/", views.assign_membership, name="assign_membership"),
    path("memberships/<int:pk>/edit/", views.membership_edit, name="membership_edit"),
    path("memberships/<int:pk>/delete/", views.membership_delete, name="membership_delete"),
    
    # Payments
    path("members/<int:member_id>/payment/", views.record_payment, name="record_payment"),
    path("payments/<int:pk>/edit/", views.payment_edit, name="payment_edit"),
    path("payments/<int:pk>/delete/", views.payment_delete, name="payment_delete"),
    
    # Expenses & Revenue
    path("expenses/", views.expense_list, name="expense_list"),
    path("expenses/new/", views.expense_create, name="expense_create"),
    path("expenses/<int:pk>/edit/", views.expense_edit, name="expense_edit"),
    path("expenses/<int:pk>/delete/", views.expense_delete, name="expense_delete"),
    path("financial-report/", views.revenue_report, name="revenue_report"),
    
    # Health Tracking
    path("members/<int:member_id>/measurements/new/", views.measurement_create, name="measurement_create"),
    path("measurements/<int:pk>/delete/", views.measurement_delete, name="measurement_delete"),
    path("members/<int:member_id>/diet-plan/", views.diet_plan_edit, name="diet_plan_edit"),
    path("members/<int:member_id>/workouts/new/", views.workout_plan_create, name="workout_plan_create"),
    path("workouts/<int:pk>/", views.workout_plan_detail, name="workout_plan_detail"),
    path("workouts/<int:pk>/delete/", views.workout_plan_delete, name="workout_plan_delete"),
    path("workouts/<int:workout_id>/exercises/new/", views.exercise_create, name="exercise_create"),
    path("exercises/<int:pk>/delete/", views.exercise_delete, name="exercise_delete"),

    # CSV Exports
    path("members/export/", views.export_members_csv, name="export_members_csv"),
    path("payments/export/", views.export_payments_csv, name="export_payments_csv"),

    # Trainers (Admin)
    path("trainers/", views.trainer_list, name="trainer_list"),
    path("trainers/new/", views.trainer_create, name="trainer_create"),
    path("trainers/<int:trainer_id>/", views.trainer_detail, name="trainer_detail"),
    path("trainers/<int:trainer_id>/edit/", views.trainer_edit, name="trainer_edit"),
    path("trainers/<int:trainer_id>/delete/", views.trainer_delete, name="trainer_delete"),
    path("members/<int:member_id>/assign-trainer/", views.assign_trainer, name="assign_trainer"),
    path("trainer/assignments/", views.trainer_assignment_list, name="trainer_assignment_list"),
    path("trainer/assignment/<int:assignment_id>/<str:action>/", views.trainer_assignment_action, name="trainer_assignment_action"),

    # Trainer Portal
    path("trainer/dashboard/", views.trainer_portal_dashboard, name="trainer_portal_dashboard"),
    path("trainer/members/", views.trainer_portal_members, name="trainer_portal_members"),

    # Admin Expansion - Classes
    path("manage/classes/", views.gym_class_list, name="admin_class_list"),
    path("manage/classes/new/", views.gym_class_create, name="admin_class_create"),
    path("manage/classes/<int:pk>/edit/", views.gym_class_edit, name="admin_class_edit"),
    path("manage/classes/<int:pk>/delete/", views.gym_class_delete, name="admin_class_delete"),

    # Admin Expansion - Equipment
    path("manage/equipment/", views.equipment_list, name="equipment_list"),
    path("manage/equipment/new/", views.equipment_create, name="equipment_create"),
    path("manage/equipment/<int:pk>/edit/", views.equipment_edit, name="equipment_edit"),
    path("manage/equipment/<int:pk>/delete/", views.equipment_delete, name="equipment_delete"),

    # Admin Expansion - Announcements
    path("manage/announcements/", views.announcement_list, name="admin_announcement_list"),
    path("manage/announcements/new/", views.announcement_create, name="admin_announcement_create"),
    path("manage/announcements/<int:pk>/edit/", views.announcement_edit, name="admin_announcement_edit"),
    path("manage/announcements/<int:pk>/delete/", views.announcement_delete, name="admin_announcement_delete"),

    # Admin Expansion - Gallery
    path("manage/gallery/", views.gym_photo_list, name="admin_gallery"),
    path("manage/gallery/<int:pk>/delete/", views.gym_photo_delete, name="admin_gallery_delete"),

    # Admin Expansion - Settings
    path("manage/settings/", views.system_settings_edit, name="system_settings"),

    # Admin Expansion - QR Check-in
    path("manage/scanner/", views.qr_scanner, name="qr_scanner"),
    path("manage/checkin-api/", views.qr_checkin_api, name="qr_checkin_api"),

    # Admin Expansion - Contact Messages
    path("manage/messages/", views.contact_message_list, name="contact_message_list"),
    path("manage/messages/<int:pk>/", views.contact_message_detail, name="contact_message_detail"),
    path("manage/messages/<int:pk>/delete/", views.contact_message_delete, name="contact_message_delete"),
]