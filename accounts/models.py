from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator, MinValueValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
from shop.models import Instrument, Order

class CustomUser(AbstractUser):
    phone_number = models.CharField(
        max_length=15,
        validators=[
            RegexValidator(
                regex=r'^\+?1?\d{9,15}$',
                message="Numarul de telefon trebuie sa fie in format: '+40 xxx xxx xxx'"
            )
        ],
        unique=True
    )
    
    birth_date = models.DateField(
        null=True,
        help_text="Format: YYYY-MM-DD"
    )
    
    address = models.TextField(
        max_length=200,
        help_text="Adresa completa de livrare"
    )
    
    newsletter = models.BooleanField(
        default=False,
        help_text="Subscrie la newsletter"
    )
    
    cod = models.CharField(max_length=100,null=True, blank=True)
    email_confirmat = models.BooleanField(default=False, null=True, blank=True)
    blocat = models.BooleanField(default=False)
    
    class Meta:
        permissions = [
            ("can_block_users", "Can block/unblock users"),
        ]

class Comanda(models.Model):
    id = models.AutoField(primary_key=True)
    order_id = models.CharField(max_length=100, unique=True, blank=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    data_comanda = models.DateTimeField(default=timezone.now)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"Comanda #{self.id} - {self.user.username}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not self.order_id:
            self.order_id = f"ORD-{self.id}"
            super().save(*args, **kwargs)

class DetaliiComanda(models.Model):
    comanda = models.ForeignKey(Comanda, on_delete=models.CASCADE, related_name='detalii')
    produs = models.ForeignKey(Instrument, on_delete=models.CASCADE)
    cantitate = models.IntegerField()
    pret_unitar = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"{self.produs.model} x {self.cantitate}"