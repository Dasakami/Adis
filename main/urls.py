from django.urls import path, include, re_path  
from rest_framework_simplejwt.views import  TokenRefreshView, TokenVerifyView


from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions


schema_view = get_schema_view(
   openapi.Info(
      title="Adis API",
      default_version='v1',
      description="Добро пожаловать! Это бета-версия, но апи работает.",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="dendasakami@gmail.com"),
      license=openapi.License(name="AAU License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

urlpatterns = [  
    re_path(r'^auth/', include('djoser.urls.authtoken')),
    path('', include('services.urls')),
    path('users/', include('users.urls')),

    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),

    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),



]  