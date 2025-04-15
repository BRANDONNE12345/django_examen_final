from django.urls import path
from . import views

app_name = 'ecommerce'

urlpatterns = [
    path('', views.shop, name='shop'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    path('product/<int:pk>/add/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart_view, name='cart'),
    path('cart/item/<int:item_id>/remove/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/item/<int:item_id>/update/', views.update_cart_item, name='update_cart_item'),
    path('cart/clear/', views.clear_cart, name='clear_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('thankyou/', views.thankyou, name='thankyou'),
    path('orders/', views.order_history, name='order_history'),
    path('orders/<int:order_id>/', views.order_detail, name='order_detail'),
    path('orders/<int:order_id>/cancel/', views.request_cancellation, name='request_cancellation'),
    path('product/<int:pk>/like/', views.toggle_like, name='toggle_like'),

    path('product/<int:pk>/avis/add/', views.add_avis, name='add_avis'),
    path('apply-promo/', views.apply_promo_code, name='apply_promo_code'),

]
