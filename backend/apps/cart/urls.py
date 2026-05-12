from django.urls import path
from .views import CartView, AddToCartView, CartItemDetailView, MergeCartView

urlpatterns = [
    path('', CartView.as_view(), name='cart-detail'),
    path('add/', AddToCartView.as_view(), name='cart-add'),
    path('item/<int:item_id>/', CartItemDetailView.as_view(), name='cart-item-detail'),
    path('merge/', MergeCartView.as_view(), name='cart-merge'),
]
