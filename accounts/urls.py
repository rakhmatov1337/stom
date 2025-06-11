from django.urls import path
from django.contrib.auth.views import LogoutView, LoginView
from .views import register, telegram_auth_view

app_name = "accounts"

urlpatterns = [
    path('register/', register, name='register'),
    path('login/', LoginView.as_view(
        template_name='auth/login.html',
        redirect_authenticated_user=True
    ), name='login'),
    path('logout/', LogoutView.as_view(next_page='accounts:login'), name='logout'),
    path('telegram-auth/', telegram_auth_view, name='telegram-auth'),
]
