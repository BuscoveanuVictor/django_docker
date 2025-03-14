from django import template
from cart_tags import Cart

register = template.Library()

@register.filter
def cart_quantity(product, request):
    cart = Cart(request)
    return cart.get_item_quantity(product.id)

@register.filter
def in_cart(product, request):
    cart = Cart(request)
    return cart.get_item_quantity(product.id) > 0