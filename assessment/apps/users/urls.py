from django.urls import path

from . import views

app_name = "users"

urlpatterns = [
    # authentication
    path('sign-up', views.SignupView.as_view(), name="user-signup"),
    path('login', views.LoginView.as_view(), name="user-login"),
]
