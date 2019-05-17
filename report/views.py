from django.shortcuts import render
from django.views.generic import TemplateView


class WarehouseProductReportView(TemplateView):
    template_name = 'reports/warehouse_product.html'