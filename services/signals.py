from django.dispatch import receiver
from django.db.models.signals import post_save
from services.models import Service, SearchHistory


@receiver(post_save, sender=Service)
def save_search_history(sender, instance, created, **kwargs):
    request = kwargs.get('request', None)
    if request and 'search' in request.GET:
        SearchHistory.objects.create(
            user=request.user,
            query=request.GET['search']
        )
