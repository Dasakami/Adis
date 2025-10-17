from django.urls import path
from .views import (
    RegisterEmailView, SendPhoneCodeView, VerifyPhoneCodeView,
    LoginEmailView, SetRoleView, MeView, UserDetailView
)
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('register/email/', RegisterEmailView.as_view(), name='register-email'),
    path('send-phone-code/', SendPhoneCodeView.as_view(), name='send-phone-code'),
    path('verify-phone-code/', VerifyPhoneCodeView.as_view(), name='verify-phone-code'),
    path('login/email/', LoginEmailView.as_view(), name='login-email'),
    path('me/', MeView.as_view(), name='me'),
    path('set-role/', SetRoleView.as_view(), name='set-role'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('<int:pk>/', UserDetailView.as_view(), name='user-detail'),
]
