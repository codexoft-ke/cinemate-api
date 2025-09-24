from django.urls import path
from . import views

urlpatterns = [
    path('login', views.LoginView.as_view(), name='login'),
    path('signup', views.SignupView.as_view(), name='signup'),
    path('forgot-password', views.ForgotPasswordView.as_view(), name='forgot-password'),
    path('forgot-password/verify', views.VerifyOTPView.as_view(), name='verify-otp'),
    path('forgot-password/change', views.ChangePasswordView.as_view(), name='change-password'),
    path('refresh-token', views.RefreshTokenView.as_view(), name='refresh-token'),
    path('logout', views.LogoutView.as_view(), name='logout'),
]