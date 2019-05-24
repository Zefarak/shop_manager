from django.urls import path
from catalogue.api.views import ProductListCreateApiView
from rest_framework_jwt.views import obtain_jwt_token
from accounts.api.views import current_user, UserList


app_name = 'api'

urlpatterns = [
    path('catalogue/product/list/', ProductListCreateApiView.as_view(), name='api_product_list'),
    path('token-auth/', obtain_jwt_token),
    path('current-user/', current_user),
    path('users/', UserList.as_view())
]