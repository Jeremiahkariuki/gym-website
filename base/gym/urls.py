from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path("members/", views.member_list, name="member_list"),
    path("new/", views.member_create, name="member_create"),
    path("login/", auth_views.LoginView.as_view (template_name="gym/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(next_page="login"),name="logout"), 
    path("dashboard/", views.dashboard, name="dashboard"),
    path("present/<int:member_id>/", views.mark_present, name="mark_present"),
    path("plans/", views.plan_list, name="plan_list"),
]