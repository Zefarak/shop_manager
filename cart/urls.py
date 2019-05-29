from django.urls import path
from .views import CartListView, CartUpdateView, check_cart_movement, ajax_cart_change_qty, CreateCartView

app_name = 'cart'

urlpatterns = [
    #  dashboard urls
    path('list/', CartListView.as_view(), name='cart_list'),
    path('create/', CreateCartView.as_view(), name='cart_create'),
    path('detail/<int:pk>/', CartUpdateView.as_view(), name='cart_detail'),

    path('check/<int:pk>/<slug:action>/', check_cart_movement, name='check'),
    path('ajax/change-qty/<int:pk>/', ajax_cart_change_qty, name='ajax_change_qty')
    ]