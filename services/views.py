from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters as drf_filters, generics
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

from .models import Category, SubCategory, Service, SearchHistory, Review, Chat, Message, UserSettings, Favorite
from .serializers import (
    CategorySerializer, FavoriteCreateSerializer, FavoriteListSerializer, SubCategorySerializer,
    ServiceListSerializer, ServiceDetailSerializer, ServiceCreateUpdateSerializer,
    ReviewSerializer, ReviewCreateSerializer,
    ChatSerializer, MessageSerializer, UserSettingsSerializer
)
from .permissions import IsOwnerOrReadOnly
from .pagination import StandardResultsSetPagination
from .filters import ServiceFilter
from django.db.models import Q

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:  # GET /categories/ и /categories/{id}/
            permission_classes = [permissions.AllowAny]
        else:  # create, update, partial_update, destroy
            permission_classes = [permissions.IsAdminUser]
        return [permission() for permission in permission_classes]


class SubCategoryViewSet(viewsets.ModelViewSet):
    queryset = SubCategory.objects.select_related('category').all()
    serializer_class = SubCategorySerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [permissions.IsAdminUser]
        return [permission() for permission in permission_classes]



class ServiceViewSet(viewsets.ModelViewSet):
    queryset = Service.objects.select_related('category', 'executor').prefetch_related('subcategories', 'photos')
    filter_backends = [DjangoFilterBackend, drf_filters.SearchFilter, drf_filters.OrderingFilter]
    filterset_class = ServiceFilter
    search_fields = ['title', 'description']
    ordering_fields = ['price', 'popularity', 'created_at']
    ordering = ['-popularity']
    pagination_class = StandardResultsSetPagination
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def get_serializer_class(self):
        if self.action in ['list']:
            return ServiceListSerializer
        if self.action in ['retrieve']:
            return ServiceDetailSerializer
        if self.action in ['create', 'update', 'partial_update']:
            return ServiceCreateUpdateSerializer
        return ServiceDetailSerializer

    def perform_create(self, serializer):
        serializer.save() 

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        search_query = request.GET.get('search')
        if search_query and request.user.is_authenticated and getattr(request.user, 'role', None) == 'client':
            SearchHistory.objects.create(user=request.user, query=search_query)
        return response

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def my_services(self, request):
        qs = self.queryset.filter(executor=request.user)
        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = ServiceListSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        serializer = ServiceListSerializer(qs, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    @method_decorator(cache_page(30)) 
    def recommended(self, request):
        """
        Рекомендации: сначала по истории поиска, потом топ популярные, если их нет — последние 1-5 созданных.
        """
        user = request.user if request.user.is_authenticated else None

        if user:
            last_search = SearchHistory.objects.filter(user=user).order_by('-created_at').first()
            if last_search:
                qs = self.queryset.filter(title__icontains=last_search.query)[:12]
                if qs.exists():
                    serializer = ServiceListSerializer(qs, many=True, context={'request': request})
                    return Response(serializer.data)

        popular_qs = self.queryset.order_by('-popularity')[:12]
        if popular_qs.exists():
            serializer = ServiceListSerializer(popular_qs, many=True, context={'request': request})
            return Response(serializer.data)

        last_created_qs = self.queryset.order_by('-created_at')[:5]
        serializer = ServiceListSerializer(last_created_qs, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def add_favorite(self, request, pk=None):
        service = self.get_object()
        user = request.user
        user.favorites.add(service)
        return Response({'status': 'added'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def remove_favorite(self, request, pk=None):
        service = self.get_object()
        user = request.user
        user.favorites.remove(service)
        return Response({'status': 'removed'}, status=status.HTTP_200_OK)



# views.py
from django_filters.rest_framework import DjangoFilterBackend

class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.select_related('author', 'service').prefetch_related('photos')
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['service']  # фильтрация по service ID

    def get_serializer_class(self):
        if self.action == 'create':
            return ReviewCreateSerializer
        return ReviewSerializer
    



class ChatViewSet(viewsets.ModelViewSet):
    queryset = Chat.objects.prefetch_related('participants', 'messages')
    serializer_class = ChatSerializer
    permission_classes = [permissions.IsAuthenticated]

class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.select_related('sender', 'chat')
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]


class UserSettingsViewSet(viewsets.ModelViewSet):
    queryset = UserSettings.objects.select_related('user')
    serializer_class = UserSettingsSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)



class FavoriteViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Favorite.objects.filter(user=self.request.user).select_related(
            'service', 'service__category'
        )

    def get_serializer_class(self):
        if self.action in ['create']:
            return FavoriteCreateSerializer
        return FavoriteListSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def destroy(self, request, *args, **kwargs):
        service_id = kwargs.get('pk')  
        favorite = Favorite.objects.filter(
            user=request.user, service_id=service_id
        ).first()

        if not favorite:
            return Response(
                {'detail': 'Эта услуга не находится в избранном.'},
                status=status.HTTP_404_NOT_FOUND
            )

        favorite.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)



class SimilarServicesView(generics.ListAPIView):
    serializer_class = ServiceDetailSerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_queryset(self):
        service_id = self.kwargs.get('service_id')

        try:
            service = Service.objects.get(id=service_id)
        except Service.DoesNotExist:
            return Service.objects.none()

        subcategory_ids = service.subcategories.values_list('id', flat=True)

        queryset = (
            Service.objects.filter(category=service.category)
            .filter(Q(subcategories__in=subcategory_ids))
            .exclude(id=service.id)
            .exclude(executor__isnull=True)
            .distinct()
            .order_by('-popularity', '-created_at')
        )

        return queryset