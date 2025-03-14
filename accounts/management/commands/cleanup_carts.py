from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from cart.models import Cart

class Command(BaseCommand):
    help = 'Șterge coșurile abandonate mai vechi de 24 ore'

    def handle(self, *args, **kwargs):
        cutoff_time = timezone.now() - timedelta(hours=24)
        deleted_count = Cart.objects.filter(
            modified__lte=cutoff_time,
            status='abandoned'
        ).delete()[0]
        
        self.stdout.write(
            self.style.SUCCESS(f'S-au șters {deleted_count} coșuri abandonate')
        )