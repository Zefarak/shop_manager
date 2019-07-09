from django.urls import path
from .views import warehouse_product_report_view, ajax_warehouse_analysis, vendor_analysis_view


app_name = 'reports'

urlpatterns = [
   path('warehouse-product-reports/', warehouse_product_report_view, name='ware_product_report'),
   path('ajax/warehouse-analysis/', ajax_warehouse_analysis, name='product_ware_analysis'),

   path('vendor-analysis/', vendor_analysis_view, name='vendor_analysis'),


]