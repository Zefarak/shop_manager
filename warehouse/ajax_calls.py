from django.shortcuts import get_object_or_404, render
from django.contrib.admin.views.decorators import staff_member_required
from django.template.loader import render_to_string
from django.http import JsonResponse, HttpResponse
from django.db.models import Sum, F, Q
from .models import Invoice
from catalogue.product_details import VendorPaycheck
from catalogue.models import Product
from site_settings.constants import CURRENCY
from .tables import ProductAddTable
from django_tables2 import RequestConfig
from .forms import BillCategoryForm, EmployeeForm

@staff_member_required
def ajax_paycheck_actions(request, question):
    data, page_title, my_data = dict(), '', []
    queryset = VendorPaycheck.filters_data(request, VendorPaycheck.objects.all())
    if question == 'value':
        total_value = queryset.aggregate(Sum('value'))['value__sum'] if queryset else 0
        paid_value = queryset.filter(is_paid=True).aggregate(Sum('value'))['value__sum'] if queryset.filter(is_paid=True) else 0
        remaining_value = total_value - paid_value
        page_title = 'Calculate Values'
        my_data = [('Total Value', total_value), ('You own', remaining_value)]
    if question == 'vendors':
        my_data = queryset.values_list('vendor__title').annotate(
            total_value=Sum('value'),
            paid_value=Sum('paid_value')
        ).order_by('total_value')
        page_title = 'Vendor Analysis'
        question = 'annotate'
    if question == 'payments':
        my_data = queryset.values_list('payment_method__title').annotate(
            total_value=Sum('value'),
            paid_value=Sum('paid_value')
        ).order_by('total_value')
        page_title = 'Payment Analysis'
        question = 'annotate'
    data['result'] = render_to_string(template_name='warehouse/ajax/invoice_results.html',
                                      request=request,
                                      context={
                                          'page_title': page_title,
                                          'my_data': my_data,
                                          'question': question,
                                          'currency': CURRENCY
                                      })
    return JsonResponse(data)


@staff_member_required
def ajax_calculate_value(request, question):
    page_title, my_data = '', []
    queryset = Invoice.objects.all()
    queryset = Invoice.filter_data(request, queryset)
    data = dict()
    if question == 'value':
        page_title = 'Analysis Value'
        total_value = queryset.aggregate(Sum('final_value'))['final_value__sum'] if queryset.exists() else 0
        paid_value = queryset.aggregate(Sum('paid_value'))['paid_value__sum'] if queryset.exists() else 0
        paid_value = total_value - paid_value
        my_data = [('Total Value', total_value), ('You own', paid_value)]
    if question == 'vendors':
        my_data = queryset.values_list('vendor__title').annotate(total=Sum('final_value'),
                                                                 paid=Sum('paid_value'),
                                                                 remaning=Sum(F('final_value')-F('paid_value')),
                                                                 ).order_by('total')
        page_title = 'Vendor analysis'
        question = 'annotate'
    data['result'] = render_to_string(request=request,
                                      template_name='warehouse/ajax/invoice_results.html',
                                      context={'page_title': page_title,
                                               'my_data': my_data,
                                               'question': question,
                                               'currency': CURRENCY
                                               }
                                      )
    return JsonResponse(data)


@staff_member_required
def ajax_search_products(request, pk):
    instance = get_object_or_404(Invoice, id=pk)
    data, search_name = dict(), request.GET.get('search_name', None)
    vendor = instance.vendor
    products = Product.my_query.active().filter(vendor=vendor)
    if search_name:
        products = products.filter(Q(title__contains=search_name) |
                                   Q(order_code__contains=search_name)
                                   ).distinct() if len(search_name) > 2 else products
    products = products[:20]
    products = ProductAddTable(products)
    RequestConfig(request).configure(products)
    data['result'] = render_to_string(template_name='warehouse/ajax/products_container.html',
                                      request=request,
                                      context={
                                          'products': products,
                                          'instance': instance
                                      }
                                    )
    return JsonResponse(data)


@staff_member_required()
def popup_new_bill(request):
    form = BillCategoryForm(request.POST or None)
    form_title = 'PopUp Λογαριασμού'
    if form.is_valid():
        instance = form.save()
        return HttpResponse(
            '<script>opener.closePopup(window, "%s", "%s", "#id_category");</script>' % (instance.pk, instance))
    return render(request, 'dashboard/form.html', context=locals())


@staff_member_required
def popup_employee(request):
    form = EmployeeForm(request.POST or None)
    if form.is_valid():
        instance = form.save()
        return HttpResponse(
            '<script>opener.closePopup(window, "%s", "%s", "#id_employee");</script>' % (instance.pk, instance))
    return render(request, 'dashboard/form.html', context=locals())