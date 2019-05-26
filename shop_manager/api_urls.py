from django.urls import path
from catalogue.api.views import ProductListCreateApiView
from rest_framework_jwt.views import obtain_jwt_token

from accounts.api.views import current_user, UserList
from point_of_sale.api.views import (OrderListApiView, OrderCreateApiView, TokenApiView, OrderItemListCreateApiView,
                                     OrderItemUpdateApiView, OrderUpdateApiView,
                                     )

app_name = 'api'

urlpatterns = [
    path('catalogue/product/list/', ProductListCreateApiView.as_view(), name='api_product_list'),
    path('token-auth/', obtain_jwt_token),
    path('current-user/', current_user),
    path('users/', UserList.as_view()),

    path('get-token/', TokenApiView.as_view()),
    path('orders/', OrderListApiView.as_view(), name='orders'),
    path('orders/create/', OrderCreateApiView.as_view()),
    path('orders/update/<int:pk>/', OrderUpdateApiView.as_view()),
    path('order-items/', OrderItemListCreateApiView.as_view()),
    path('order-item/update/<int:pk>/', OrderItemUpdateApiView.as_view()),
]