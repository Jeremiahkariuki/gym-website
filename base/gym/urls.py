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
    
    # Payments
    path("members/<int:member_id>/payment/", views.record_payment, name="record_payment"),
    path("revenue-report/", views.revenue_report, name="revenue_report"),
]