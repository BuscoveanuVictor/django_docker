from django.core.management.base import BaseCommand
from shop.models import Product
from django.core.mail import send_mail

class Command(BaseCommand):
    help = 'Verifică stocul produselor și trimite alerte'

    def handle(self, *args, **kwargs):
        low_stock_products = Product.objects.filter(stock__lte=5, active=True)
        
        if low_stock_products.exists():
            message = "Produse cu stoc redus:\n\n"
            for product in low_stock_products:
                message += f"- {product.name}: {product.stock} bucăți\n"
            
            send_mail(
                'Alertă stoc redus',
                message,
                'noreply@yoursite.com',
                ['admin@yoursite.com'],
                fail_silently=False,
            )
        
        self.stdout.write(
            self.style.SUCCESS(f'Verificare stoc completă. {low_stock_products.count()} produse cu stoc redus.')
        )