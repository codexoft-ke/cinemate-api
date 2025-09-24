from django.urls import path
from . import views

urlpatterns = [
    path('', views.ProfileView.as_view(), name='profile'),
    path('change-password', views.ChangePasswordView.as_view(), name='change-password'),
    path('notifications', views.NotificationsView.as_view(), name='notifications'),
    path('notifications/read', views.MarkNotificationReadView.as_view(), name='mark-notifications-read'),
]