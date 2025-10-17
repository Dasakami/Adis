import django_filters
from .models import Service

class ServiceFilter(django_filters.FilterSet):
    min_price = django_filters.NumberFilter(field_name="price", lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name="price", lookup_expr='lte')
    category = django_filters.NumberFilter(field_name="category__id")
    subcategory = django_filters.NumberFilter(field_name="subcategories__id")
    experience = django_filters.CharFilter(field_name="experience")

    class Meta:
        model = Service
        fields = ['category', 'subcategory', 'experience', 'min_price', 'max_price']
