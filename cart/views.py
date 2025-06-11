# cart/views.py

from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from main.models import ProductVariant
from .models import Cart, CartItem


@login_required
@require_POST
def add_to_cart(request):
    product_id = request.POST.get("product_id")
    variant_id = request.POST.get("variant_id")

    if not product_id or not variant_id:
        return JsonResponse({"error": "Product ID and Variant ID are required."}, status=400)

    product_variant = get_object_or_404(
        ProductVariant, id=variant_id, product_id=product_id)
    cart, _ = Cart.objects.get_or_create(user=request.user)

    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product_variant=product_variant,
        defaults={"quantity": 0}
    )

    cart_item.quantity += 1
    cart_item.save()
    total_items = sum(item.quantity for item in cart.items.all())

    return redirect('main:cart')


@login_required
@require_POST
def update_cart(request):
    product_id = request.POST.get("product_id")
    size_id = request.POST.get("size_id")

    try:
        quantity = int(request.POST.get("quantity", 0))
    except (ValueError, TypeError):
        quantity = 0

    cart, _ = Cart.objects.get_or_create(user=request.user)
    product_variant = get_object_or_404(
        ProductVariant, product_id=product_id, size_id=size_id)

    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product_variant=product_variant,
        defaults={'quantity': 0}
    )

    if quantity <= 0:
        cart_item.delete()
        updated_quantity = 0
    else:
        cart_item.quantity = quantity
        cart_item.save()
        updated_quantity = cart_item.quantity

    cart_items = cart.items.select_related('product_variant').all()
    total_cost = sum(item.product_variant.price *
                     item.quantity for item in cart_items)

    return JsonResponse({
        "updated_quantity": updated_quantity,
        "total_items": sum(item.quantity for item in cart_items),
        "total_cost": total_cost
    })


@login_required
def cart_count_api(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    total_items = sum(item.quantity for item in cart.items.all())
    return JsonResponse({'total_items': total_items})
