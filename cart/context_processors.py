from .models import Cart

def cart_item_count(request):
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
        return {'cart_item_count': sum(item.quantity for item in cart.items.all())}
    return {'cart_item_count': 0}