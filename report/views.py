from django.shortcuts import render
from django.views.generic import TemplateView
from django.utils.decorators import method_decorator
from django.db.models import Sum
from django.contrib.admin.views.decorators import staff_member_required
from django.template.loader import render_to_string
from django.http import JsonResponse

from catalogue.models import Product, WarehouseCategory, Vendor, Brand
from point_of_sale.models import OrderItem
from warehouse.models import InvoiceOrderItem
from .tools import date_range_filter


@staff_member_required
def warehouse_product_report_view(request):
    date_start, date_end = date_range_filter(request)
    products = Product.objects.none()
    if 'get_button' in request.GET:
        products = Product.filters_data(request, Product.objects.filter(active=True))
    vendor_filter, date_filter, search_filter = [True]*3
    vendors, categories = Vendor.objects.filter(active=True), WarehouseCategory.objects.filter(active=True)

    # get warehouse
    warehouse_data = InvoiceOrderItem.objects.filter(order__date_expired__range=[date_start, date_end],
                                                     product__in=products
                                                     )
    warehouse_movement = warehouse_data.values_list('product__title').annotate(qty=Sum('qty'),
                                                                               total_value=Sum('total_final_value')
                                                                               ).order_by('product__title') \
        if warehouse_data else 'No data'

    #  get sells
    sells_data = OrderItem.objects.filter(order__date_expired__range=[date_start, date_end], title__in=products)
    sell_movements = sells_data.values_list('title__title', 'title__vendor__title')\
        .annotate(qty=Sum('qty'),
                  total_cost=Sum('total_cost_value'),
                  total_value=Sum('total_value')
                ).order_by('title__title')

    return render(request, 'reports/warehouse_product.html', context=locals())


@staff_member_required
def ajax_warehouse_analysis(request):
    print('here')
    data = dict()
    products = Product.filters_data(request, Product.objects.all())
    queryset = InvoiceOrderItem.objects.filter(product__in=products)
    queryset_table = queryset.values_list('product__title', 'product__qty','product__vendor')\
        .annotate(qty=Sum('qty'),
                  total_value=Sum('total_final_value')
                ).order_by('product__title') \
        if queryset else 'No data'
    print(queryset_table)
    data['result_analysis'] = render_to_string(template_name='reports/ajax_analysis.html',
                                               request=request,
                                               context={
                                                 'queryset_table': queryset_table
                                               })
    return JsonResponse(data)


@staff_member_required
def vendor_analysis_view(request):
    vendors = Vendor.objects.filter(active=True)
    return render(request, 'reports/vendor_report.html', context=locals())
