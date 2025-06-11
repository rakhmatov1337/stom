from django.urls import path

from .views import add_to_cart,update_cart,cart_count_api
app_name = "cart"

urlpatterns = [
    path('add/', add_to_cart, name='add-to-cart'),
    path('cart/update/', update_cart, name='update-cart'),
    path('count/', cart_count_api, name='cart-count'), 
]
    