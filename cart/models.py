from decimal import Decimal
from django.conf import settings
from shop.models import Instrument
class Cart:
    def add(self, product, quantity=1):
        product_id = str(product.id)
        
        if quantity > product.stock:
            return False, "Cantitatea ceruta depaseste stocul disponibil"
            
        if product_id not in self.cart:
            self.cart[product_id] = {'quantity': 0, 'price': str(product.price)}
            
        if self.cart[product_id]['quantity'] + quantity > product.stock:
            return False, "Nu mai exista suficient stoc disponibil"
            
        self.cart[product_id]['quantity'] += quantity
        self.save()
        return True, "Produs adaugat cu succes"

    def update_quantity(self, product, quantity):
        product_id = str(product.id)
        if quantity > product.stock:
            return False, "Cantitatea ceruta depaseste stocul disponibil"
            
        if quantity > 0:
            self.cart[product_id]['quantity'] = quantity
        else:
            del self.cart[product_id]
        self.save()
        return True, "Cantitate actualizata cu succes"
    
    def save(self):
        self.session[settings.CART_SESSION_ID] = self.cart
        self.session.modified = True