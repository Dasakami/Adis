from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import (
    CategoryViewSet, FavoriteViewSet, SimilarServicesView, SubCategoryViewSet,
    ServiceViewSet, ReviewViewSet,
    ChatViewSet, MessageViewSet,
    UserSettingsViewSet
)

router = DefaultRouter()
router.register(r'categories', CategoryViewSet)
router.register(r'subcategories', SubCategoryViewSet)
router.register(r'services', ServiceViewSet, basename='service')
router.register(r'reviews', ReviewViewSet)
router.register(r'chats', ChatViewSet)
router.register(r'messages', MessageViewSet)
router.register(r'settings', UserSettingsViewSet)
router.register(r'favorites', FavoriteViewSet, basename='favorite')

urlpatterns = [
    path('', include(router.urls)),
    path('similar/<int:service_id>/', SimilarServicesView.as_view(), name='similar-services'),
]
