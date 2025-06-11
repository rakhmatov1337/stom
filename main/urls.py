from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from .views import *

app_name = "main"

urlpatterns = [
    path("", HomePageView.as_view(), name="home"),
    path('cart/', CartView.as_view(), name='cart'),
    path('cart/update/', update_cart, name='update-cart-ajax'),
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('ordeer/<int:pk>/', OrderDetailView.as_view(), name='order-detail'),
    path('create-order/', CreateOrderView.as_view(), name='create-order'),
    path('favorite/add/', AddToFavoriteView.as_view(), name='add-to-favorite'),
    path('favorite/', FavoriteListView.as_view(), name='favorite-list'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path("my-orders/", MyOrdersView.as_view(), name="my-orders"),
    path("search/", SearchView.as_view(), name="product_search"),
    path('product/<int:pk>/', ProductDetailView.as_view(), name='product-detail'),
    
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)