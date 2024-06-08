from django.urls import path
from user.views import CookieTokenRefreshView, logoutView, user, getSubscriptions, RegisterView, LoginView

app_name = "user"

urlpatterns = [
    path('logout', logoutView),
    path('user', user),
    path('subscriptions', getSubscriptions),
    path('refresh-token', CookieTokenRefreshView.as_view(), name='refresh-token'),
    path('register', RegisterView.as_view(), name='register'),
    path('login', LoginView.as_view(), name='login'),
]
