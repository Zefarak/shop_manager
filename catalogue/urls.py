from .autocomplete_widgets import VendorAutocomplete, WarehouseCategoryAutocomplete
from django.urls import path
from .api.views import ProductListCreateApiView


urlpatterns = [
    path('vendors/', VendorAutocomplete.as_view(), name='vendors_auto'),
    path('warehouse/', WarehouseCategoryAutocomplete.as_view(), name='warehouse_category_auto'),


    #  api urls
    path('api/catalogue/product/list/', ProductListCreateApiView.as_view(), name='api_product_list'),

]