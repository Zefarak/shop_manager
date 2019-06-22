from django.shortcuts import get_object_or_404, render
from django.contrib.admin.views.decorators import staff_member_required
from django.template.loader import render_to_string
from django.http import JsonResponse, HttpResponse
from django.db.models import Sum, F, Q
from .models import Invoice, InvoiceOrderItem, InvoiceAttributeItem
from catalogue.product_details import VendorPaycheck
from catalogue.models import Product
from catalogue.product_attritubes import Attribute, AttributeProductClass, AttributeTitle
from site_settings.constants import CURRENCY
from .tables import ProductAddTable, InvoiceAttributeItemTable
from django_tables2 import RequestConfig
from .forms import BillCategoryForm, EmployeeForm, OccupationForm, GenericExpenseCategoryForm, GenericPersonForm
from decimal import Decimal

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


@staff_member_required
def ajax_add_attr_to_invoice_view(request, pk, dk):
    print(request.POST)
    # getting the values
    invoice = get_object_or_404(Invoice, id=pk)
    product = get_object_or_404(Product, id=dk)
    value = request.POST.get('value', None)
    discount = request.POST.get('discount', None)

    # create the order item
    order_item, created = InvoiceOrderItem.objects.get_or_create(order=invoice, product=product)

    # get the attribute class
    attr_product_class = product.attr_class.filter(class_related__have_transcations=True).first()

    for ele in request.POST:
        if ele.startswith('qty_'):
            get_id = ele.split('_')[1]
            qty = request.POST.get(ele, None)
            if qty:
                qty = Decimal(qty)
                if qty > 0:
                    attr_title = get_object_or_404(AttributeTitle, id=get_id)
                    product_attribute, created = Attribute.objects.get_or_create(title=attr_title,
                                                                                 class_related=attr_product_class
                                                                                 )
                    product_attribute.price_buy = value
                    product_attribute.order_discount = discount
                    product_attribute.qty = qty
                    product_attribute.save()
                    attr_invoice, created = InvoiceAttributeItem.objects.get_or_create(order_item=order_item,
                                                                                       attribute_related=product_attribute
                                                                                       )
                    if created:
                        attr_invoice.qty = qty
                    else:
                        attr_invoice.qty = attr_invoice.qty + qty
                    attr_invoice.save()
    data = dict()

    order_item.value = Decimal(value) if value else 0
    order_item.discount_value = Decimal(discount) if discount else 0
    product.price_buy = Decimal(value) if value else product.price_buy
    product.order_discount = Decimal(discount) if discount else product.order_discount
    product.order_code = request.POST.get('order_code', product.order_code)
    product.save()
    order_item.save()
    order_item.refresh_from_db()
    selected_data = order_item.my_attributes.all()
    data['result'] = render_to_string(template_name='warehouse/ajax/invoice_result_data.html',
                                      request=request,
                                      context={
                                          'selected_data': selected_data
                                      })
    return JsonResponse(data)


@staff_member_required
def ajax_edit_invoice_attr_view(request, pk):
    data = dict()
    attr_order_item = get_object_or_404(InvoiceAttributeItem, id=pk)
    qty = request.GET.get('qty', None)
    if qty:
        qty = Decimal(qty)
        if qty > 0:
            attr_order_item.qty = qty
            attr_order_item.save()
        else:
            attr_order_item.delete()
    order_item = attr_order_item.order_item
    order_item.save()
    order_item.refresh_from_db()
    selected_data = order_item.my_attributes.all()
    data['result'] = render_to_string(template_name='warehouse/ajax/invoice_result_data.html',
                                      request=request,
                                      context={
                                          'selected_data': selected_data
                                      })
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


@staff_member_required
def popup_occupation(request):
    form = OccupationForm(request.POST or None)
    if form.is_valid():
        instance = form.save()
        return HttpResponse(
            '<script>opener.closePopup(window, "%s", "%s", "#id_occupation");</script>' % (instance.pk, instance))
    return render(request, 'dashboard/form.html', context=locals())


@staff_member_required
def popup_generic_category(request):
    form = GenericExpenseCategoryForm(request.POST or None)
    if form.is_valid():
        instance = form.save()
        return HttpResponse(
            '<script>opener.closePopup(window, "%s", "%s", "#id_category");</script>' % (instance.pk, instance))
    return render(request, 'dashboard/form.html', context=locals())


@staff_member_required
def popup_generic_person(request):
    form = GenericPersonForm(request.POST or None)
    if form.is_valid():
        instance = form.save()
        return HttpResponse(
            '<script>opener.closePopup(window, "%s", "%s", "#id_person");</script>' % (instance.pk, instance))
    return render(request, 'dashboard/form.html', context=locals())