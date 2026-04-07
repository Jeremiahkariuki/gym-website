from django.urls import path
from django.contrib.auth import views as auth_views
from django.views.generic import RedirectView
from . import views

urlpatterns = [
    # Root
    path("", RedirectView.as_view(url='login/', permanent=False), name="home"),
    
    # Members
    path("members/", views.member_list, name="member_list"),
    path("members/new/", views.member_create, name="member_create"),
    path("members/<int:member_id>/", views.member_detail, name="member_detail"),
    path("members/<int:member_id>/edit/", views.member_edit, name="member_edit"),
    path("members/<int:member_id>/delete/", views.member_delete, name="member_delete"),
    
    # Authentication
    path("login/", auth_views.LoginView.as_view(template_name="gym/login.html", form_class=views.LoginForm), name="login"),
    path("register/", views.register_view, name="register"),
    path("logout/", views.logout_view, name="logout"), 
    
    # Dashboard
    path("dashboard/", views.dashboard, name="dashboard"),
    
    # Attendance
    path("present/<int:member_id>/", views.mark_present, name="mark_present"),
    path("attendance-report/", views.attendance_report, name="attendance_report"),
    
    # Plans
    path("plans/", views.plan_list, name="plan_list"),
    path("plans/new/", views.plan_create, name="plan_create"),
    
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
]