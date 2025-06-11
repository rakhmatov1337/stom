from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator
from django.http import JsonResponse
from django.utils import timezone
from django.utils.timezone import localtime
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.views.generic import ListView, DetailView, TemplateView
from django.utils.html import escape


from .models import *
from cart.models import CartItem, Cart
from .tasks import TelegramBotService


class HomePageView(ListView):
    template_name = "index.html"
    model = Product
    context_object_name = "products"

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user.is_authenticated:
            for product in queryset:
                product.is_favorite = Favorite.objects.filter(
                    user=self.request.user, product=product).exists()
        else:
            for product in queryset:
                product.is_favorite = False
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['bigpics'] = BigPic.objects.all()
        return context


class CartView(LoginRequiredMixin, View):
    def get(self, request):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        cart_items = cart.items.select_related('product_variant').all()
        total_cost = sum(item.product_variant.price *
                         item.quantity for item in cart_items)
        delivery_cost = 0 if total_cost >= 1000000 else 30000
        grand_total = total_cost + delivery_cost

        context = {
            'cart': cart,
            'cart_items': cart_items,
            'total_cost': total_cost,
            'delivery_cost': delivery_cost,
            'grand_total': grand_total,
        }
        return render(request, 'cart.html', context)


@login_required
@require_POST
def update_cart(request):
    product_id = request.POST.get("product_id")
    size_id = request.POST.get("size_id")
    quantity = int(request.POST.get("quantity", 0))

    variant = get_object_or_404(ProductVariant, product_id=product_id, size_id=size_id)
    cart, _ = Cart.objects.get_or_create(user=request.user)

    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product_variant=variant,
        defaults={"quantity": 0}
    )

    if quantity <= 0:
        cart_item.delete()
        updated_quantity = 0
    else:
        cart_item.quantity = quantity
        cart_item.save()
        updated_quantity = cart_item.quantity

    cart_items = cart.items.select_related('product_variant').all()
    total_cost = sum(item.product_variant.price * item.quantity for item in cart_items)
    delivery_cost = 0 if total_cost >= 1_000_000 else 30_000
    grand_total = total_cost + delivery_cost

    return JsonResponse({
        "updated_quantity": updated_quantity,
        "total_items": sum(item.quantity for item in cart_items),
        "total_cost": total_cost,
        "delivery_cost": delivery_cost,
        "grand_total": grand_total,
    })

class CheckoutView(LoginRequiredMixin, View):
    def post(self, request):
        cart = get_object_or_404(Cart, user=request.user)
        cart_items = cart.items.select_related('product').all()
        if not cart_items.exists():
            return redirect('cart:cart')

        total_cost = sum(item.product.price *
                         item.quantity for item in cart_items)
        delivery_cost = 0 if total_cost >= 1000000 else 30000
        grand_total = total_cost + delivery_cost
        order = Order.objects.create(
            user=request.user,
            delivery_cost=delivery_cost,
            total_cost=grand_total,
            address="Tashkent, Tashkent",
            phone="+998901234567",
            full_name="John Doe",
        )

        return redirect('cart:order-detail', pk=order.id)


class OrderDetailView(LoginRequiredMixin, DetailView):
    model = Order
    template_name = 'order-detail.html'
    context_object_name = 'order'

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['order_items'] = self.object.items.select_related('product')
        return context


@method_decorator(login_required, name='dispatch')
class CreateOrderView(View):
    def post(self, request):
        cart = get_object_or_404(Cart, user=request.user)
        cart_items = cart.items.select_related('product_variant__product', 'product_variant__size')

        if not cart_items.exists():
            return redirect('main:cart')

        phone = request.POST.get('phone_number')
        address = request.POST.get('address')

        # Step 1: Create the order first
        order = Order.objects.create(
            user=request.user,
            total_price=0,  # will be updated later
            status='pending',
            created_at=timezone.now(),
            phone_number=phone,
            address=address
        )

        total_cost_uzs = 0
        total_cost_usd = 0
        user_item_lines = []
        admin_item_lines = []

        for item in cart_items:
            variant = item.product_variant
            product = variant.product
            size = variant.size

            total_item_uzs = variant.price * item.quantity
            total_item_usd = (variant.price_usd or 0) * item.quantity

            total_cost_uzs += total_item_uzs
            total_cost_usd += total_item_usd

            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=item.quantity,
                price=variant.price,
                size=size
            )

            user_line = f"🛒 <b>Mahsulot:</b> {escape(product.name)} ({size.name})\n🔢 <b>Soni:</b> {item.quantity}"
            user_line += f"\n🇺🇿 <b>Narx:</b> {variant.price:,.0f} x {item.quantity} = {total_item_uzs:,.0f} UZS"
            if variant.price_usd:
                user_line += f"\n💵 <b>Narx (USD):</b> {variant.price_usd:.2f} x {item.quantity} = {total_item_usd:.2f} USD"
            user_item_lines.append(user_line)

            admin_line = f"🛒 <b>Mahsulot:</b> {escape(product.name)} (ID: {product.id}) ({size.name})\n🔢 <b>Soni:</b> {item.quantity}"
            admin_line += f"\n🇺🇿 {variant.price:,.0f} x {item.quantity} = {total_item_uzs:,.0f} UZS"
            if variant.price_usd:
                admin_line += f"\n💵 {variant.price_usd:.2f} x {item.quantity} = {total_item_usd:.2f} USD"
            admin_item_lines.append(admin_line)


        # Delivery
        delivery_cost = 0 if total_cost_uzs >= 1_000_000 else (30_000 if total_cost_uzs > 0 else 0)
        grand_total_uzs = total_cost_uzs + delivery_cost

        # Update order price
        order.total_price = grand_total_uzs
        order.save()

        # Clear cart
        cart.items.all().delete()

        # Format messages
        user_items_text = "\n\n".join(user_item_lines)
        admin_items_text = "\n\n".join(admin_item_lines)

        user_message = (
            f"✅ <b>Buyurtmangiz qabul qilindi!</b>\n"
            f"🆔 ID: #{order.pk}\n"
            f"📦 Buyurtma tafsilotlari:\n\n{user_items_text}\n\n"
            f"🚚 <b>Yetkazib berish:</b> {delivery_cost:,.0f} UZS\n"
            f"💰 <b>Umumiy:</b> {grand_total_uzs:,.0f} UZS"
        )
        if total_cost_usd > 0:
            user_message += f"\n💵 <b>Umumiy (USD):</b> {total_cost_usd:.2f} USD"
        user_message += "\n\nTez orada adminlarimiz siz bilan bogʻlanadi."

        admin_message = (
            f"📥 <b>Yangi buyurtma</b>\n"
            f"👤 <b>Foydalanuvchi:</b> {escape(request.user.get_full_name())} (ID: {request.user.id})\n"
            f"📞 <b>Tel:</b> {phone}\n"
            f"📍 <b>Manzil:</b> {escape(address)}\n"
            f"🆔 <b>Buyurtma ID:</b> #{order.pk}\n\n"
            f"📦 <b>Buyurtma tafsilotlari:</b>\n\n{admin_items_text}\n\n"
            f"🚚 <b>Yetkazib berish:</b> {delivery_cost:,.0f} UZS\n"
            f"💰 <b>Umumiy:</b> {grand_total_uzs:,.0f} UZS"
        )
        if total_cost_usd > 0:
            admin_message += f"\n💵 <b>Umumiy (USD):</b> {total_cost_usd:.2f} USD"

        # Send messages
        if request.user.phone_number:
            try:
                TelegramBotService.send_to_user(request.user.phone_number, user_message)
            except Exception:
                pass

        TelegramBotService.send_to_admin(admin_message)

        return redirect('main:home')
        
        
class AddToFavoriteView(LoginRequiredMixin, View):
    def post(self, request):
        product_id = request.POST.get('product_id')
        product = get_object_or_404(Product, id=product_id)
        fav, created = Favorite.objects.get_or_create(
            user=request.user, product=product)
        if not created:
            fav.delete()
            return JsonResponse({'status': 'removed'})
        return JsonResponse({'status': 'added'})


class FavoriteListView(LoginRequiredMixin, View):
    def get(self, request):
        favorites = Favorite.objects.filter(
            user=request.user).select_related('product')
        return render(request, 'fav-products.html', {'favorites': favorites})


class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_order'] = Order.objects.filter(
            user=self.request.user).order_by('-created_at').first()
        return context


class MyOrdersView(LoginRequiredMixin, ListView):
    template_name = "my-orders.html"
    context_object_name = "orders"

    def get_queryset(self):
        orders = Order.objects.filter(user=self.request.user).prefetch_related(
            'items__product').order_by('-created_at')
        for order in orders:
            order.created_at_local = localtime(order.created_at)
        return orders


class SearchView(ListView):
    template_name = "result-product.html"
    model = Product
    context_object_name = "products"

    def get_queryset(self):
        query = self.request.GET.get("q", "").strip()
        if query:
            return Product.objects.filter(
                Q(name__icontains=query) |
                Q(category__name__icontains=query)
            ).select_related('category')
        return Product.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["query"] = self.request.GET.get("q", "")
        return context


class ProductDetailView(DetailView):
    model = Product
    template_name = 'detail.html'
    context_object_name = 'product'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['variants'] = self.object.variants.select_related('size')
        return context




