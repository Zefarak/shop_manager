from django.urls import path
from .views import WarehouseProductReportView


app_name = 'reports'

urlpatterns = [
   path('warehouse-product-reports/', WarehouseProductReportView.as_view(), name='ware_product_report'),

]