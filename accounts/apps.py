from django.apps import AppConfig
from django.db.models.signals import post_migrate
import schedule
import time
from datetime import datetime, timedelta
from django.core.mail import send_mass_mail
from django.conf import settings
import threading
import logging

logger = logging.getLogger(__name__)

class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'
    verbose_name = 'Conturi Utilizatori'

    def delete_unconfirmed_users(self):
        """Șterge utilizatorii neconfirmați"""
        try:
            users = self.get_model('CustomUser').objects.filter(
                email_confirmed=False,
                date_joined__lte=datetime.now() - timedelta(minutes=2)
            )
            count = users.count()
            users.delete()
            logger.info(f"S-au șters {count} utilizatori neconfirmați")
        except Exception as e:
            logger.error(f"Eroare la ștergerea utilizatorilor neconfirmați: {e}")

   
    def check_inactive_users(self):
        """Verifică utilizatorii inactivi"""
        try:
            inactive_users = self.get_model('CustomUser').objects.filter(
                last_login__lte=datetime.now() - timedelta(days=30)
            )
            for user in inactive_users:
                user.email_user(
                    'Te extragerăm!',
                    'Nu ai mai fost activ de 30 de zile. Te așteptăm înapoi!',
                    settings.DEFAULT_FROM_EMAIL
                )
            logger.info(f"Email-uri trimise la {inactive_users.count()} utilizatori inactivi")
        except Exception as e:
            logger.error(f"Eroare la verificarea utilizatorilor inactivi: {e}")

    def daily_user_stats(self):
        """Generează statistici zilnice"""
        try:
            CustomUser = self.get_model('CustomUser')
            total_users = CustomUser.objects.count()
            new_users = CustomUser.objects.filter(
                date_joined__date=datetime.now().date()
            ).count()
            
            from django.core.mail import mail_admins
            mail_admins(
                'Statistici zilnice utilizatori',
                f'Total utilizatori: {total_users}\n'
                f'Utilizatori noi azi: {new_users}',
                fail_silently=False
            )
            logger.info("Statistici zilnice generate și trimise")
        except Exception as e:
            logger.error(f"Eroare la generarea statisticilor: {e}")

    def run_scheduler(self):
        """Rulează scheduler-ul"""
        while True:
            schedule.run_pending()
            time.sleep(1)

    def start_schedulers(self):
        """Configurează și pornește toate task-urile programate"""
        # Configurare task-uri
        schedule.every().day.do(self.delete_unconfirmed_users)
        schedule.every(30).minutes.do(self.check_inactive_users)
        schedule.every().day.at("23:00").do(self.daily_user_stats)

        # Pornește scheduler-ul într-un thread separat
        thread = threading.Thread(target=self.run_scheduler, daemon=True)
        thread.start()
        logger.info("Scheduler pornit cu succes")

    def ready(self):
        """Metoda apelată când aplicația este gata"""
        # Pornește task-urile programate
        self.start_schedulers()

         # Conectăm semnalul pentru crearea grupurilor
        post_migrate.connect(self.create_default_groups, sender=self)
        
    def create_default_groups(self, *args, **kwargs):
        """Creează grupurile implicite după migrare"""
        from django.contrib.auth.models import Group, Permission
        from django.contrib.auth import get_user_model
        from django.contrib.contenttypes.models import ContentType
        
        # Grup pentru moderatori
        moderatori_group, created = Group.objects.get_or_create(name='Moderatori')
        if created:
            # Obținem modelul CustomUser
            CustomUser = get_user_model()
            content_type = ContentType.objects.get_for_model(CustomUser)
            
            # Permisiuni pentru moderatori
            moderatori_group.permissions.add(
                # Permisiune de vizualizare utilizatori
                Permission.objects.get(
                    content_type=content_type,
                    codename='view_customuser'
                ),
                # Permisiune de editare utilizatori
                Permission.objects.get(
                    content_type=content_type,
                    codename='change_customuser'
                ),
                # Permisiune de blocare/deblocare utilizatori
                Permission.objects.get(
                    content_type=content_type,
                    codename='can_block_users'
                )
            )
            
            # Setăm is_staff=True pentru moderatori (nu mai folosim view_site)
            CustomUser.objects.filter(groups=moderatori_group).update(is_staff=True)
            
            logger.info("Grup 'Moderatori' creat cu succes")
        
       
