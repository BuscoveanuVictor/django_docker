from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from accounts.models import CustomUser

class Command(BaseCommand):
    help = 'Șterge utilizatorii care nu au confirmat emailul'

    def handle(self, *args, **kwargs):
        cutoff_time = timezone.now() - timedelta(minutes=2)
        deleted_count = CustomUser.objects.filter(
            email_confirmed=False,
            date_joined__lte=cutoff_time
        ).delete()[0]
        
        self.stdout.write(
            self.style.SUCCESS(f'S-au șters {deleted_count} utilizatori neconfirmați')
        )