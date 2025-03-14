from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from django.core.mail import send_mass_mail
from accounts.models import CustomUser

class Command(BaseCommand):
    help = 'Trimite newsletter către utilizatorii vechi'

    def handle(self, *args, **kwargs):
        # Utilizatori mai vechi de 30 minute
        users = CustomUser.objects.filter(
            date_joined__lte=timezone.now() - timedelta(minutes=30),
            is_active=True,
            email_confirmed=True
        )
        
        emails = [(
            'Newsletter săptămânal',
            'Bună ziua! Iată noutățile săptămânii...',
            'noreply@yoursite.com',
            [user.email]
        ) for user in users]
        
        send_mass_mail(emails, fail_silently=False)
        
        self.stdout.write(
            self.style.SUCCESS(f'Newsletter trimis la {len(emails)} utilizatori')
        )