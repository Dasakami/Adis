from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete
from services.models import Review, Service, SearchHistory
from django.db.models import Avg, Count 

@receiver(post_save, sender=Service)
def save_search_history(sender, instance, created, **kwargs):
    request = kwargs.get('request', None)
    if request and 'search' in request.GET:
        SearchHistory.objects.create(
            user=request.user,
            query=request.GET['search']
        )

@receiver([post_save, post_delete], sender=Review)
def update_service_rating(sender, instance, **kwargs):
    service = instance.service
    agg = service.reviews.aggregate(avg=Avg('rating'), count=Count('id'))
    service.average_rating = agg['avg'] or 0
    service.review_count = agg['count'] or 0
    service.save(update_fields=['average_rating', 'review_count'])

