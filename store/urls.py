from django.urls import path

from store.apps import StoreConfig
from store.views import index, about, contact, ProductList, ProductDetail, info, CartDetailView, \
    AddToCartView, UpdateCartItemView, RemoveFromCartView, FavouriteList, AddFavouriteView, \
    RemoveFavouriteView, returns, CreateOrderView, OrderDetailView, OrderSuccessView, CancelOrderView

app_name = StoreConfig.name

urlpatterns = [
    path('', index, name='index'),
    path('about/', about, name='about'),
    path('contact/', contact, name='contact'),
    path('products/', (ProductList.as_view()), name='product_list'),
    path('products/mens/', ProductList.as_view(), {'gender': 'M'}, name='mens_products'),
    path('products/womens/', ProductList.as_view(), {'gender': 'F'}, name='womens_products'),
    path('products/unisex/', ProductList.as_view(), {'gender': 'U'}, name='unisex_products'),
    path('products/<slug:slug>/', ProductDetail.as_view(), name='product_detail'),
    path('info/', info, name='info'),
    path('returns/', returns, name='returns'),
    path('cart/', CartDetailView.as_view(), name='cart_detail'),
    path('cart/add/', AddToCartView.as_view(), name='add_to_cart'),
    path('cart/update/', UpdateCartItemView.as_view(), name='update_cart_item'),
    path('cart/remove/', RemoveFromCartView.as_view(), name='remove_from_cart'),
    path('favourite/', FavouriteList.as_view(), name='favourite_list'),
    path('favourite/add/', AddFavouriteView.as_view(), name='add_favourite'),
    path('favourite/remove/', RemoveFavouriteView.as_view(), name='remove_favourite'),
    path('order/create/', CreateOrderView.as_view(), name='create_order'),
    path('order/<int:order_id>/', OrderDetailView.as_view(), name='order_detail'),
    path('order/success/', OrderSuccessView.as_view(), name='order_success'),
    path('order/<int:order_id>/cancel/', CancelOrderView.as_view(), name='cancel_order'),  # Новый маршрут

]
