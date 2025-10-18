
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
from rest_framework_simplejwt.views import  TokenRefreshView, TokenVerifyView, TokenObtainPairView
urlpatterns = [
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}), 
    re_path(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT}),
    path('admin/', admin.site.urls),
    path('api/', include('main.urls')),

    path('api/auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
   path('api/auth/social/', include('allauth.socialaccount.urls')),
   path('api/auth/djoser/', include('djoser.urls')),
   path('api/auth/djoser/token/', include('djoser.urls.authtoken')),
   path('api/auth/registration/', include('dj_rest_auth.registration.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
