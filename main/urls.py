from django.urls import path, include, re_path  
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView


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


urlpatterns = [  
    re_path(r'^auth/', include('djoser.urls.authtoken')),
    path('', include('services.urls')),
    path('users/', include('users.urls')),

    path('auth/', include('djoser.urls')),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),

    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]  