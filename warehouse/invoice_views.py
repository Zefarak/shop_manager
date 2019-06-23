from django.shortcuts import reverse, redirect, render, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, UpdateView, CreateView
from django.utils.decorators import method_decorator
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Sum
from django.contrib import messages
from .models import Invoice, InvoiceOrderItem, InvoiceImage, VendorPaycheck
from catalogue.models import Product
from catalogue.product_details import Vendor
from catalogue.forms import VendorForm
from site_settings.constants import CURRENCY
from .forms import CreateInvoiceForm, UpdateInvoiceForm, CreateOrderItemForm, InvoiceImageForm, CopyInvoiceForm, InvoiceAttributeCreateOrEditForm
from .tables import InvoiceImageTable, InvoiceTable, VendorTable, ProductAddTable

from django_tables2 import RequestConfig


@method_decorator(staff_member_required, name='dispatch')
class WarehouseOrderList(ListView):
    model = Invoice
    template_name = 'dashboard/list_page.html'
    paginate_by = 50

    def get_queryset(self):
        queryset = Invoice.objects.all()
        queryset = Invoice.filter_data(self.request, queryset)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        queryset_table = InvoiceTable(self.object_list)
        RequestConfig(self.request).configure(queryset_table)
        vendors = Vendor.objects.filter(active=True)
        vendor_filter = True
        page_title, create_url, back_url = 'Τιμολόγια', reverse('warehouse:create_invoice'), reverse('warehouse:dashboard')
        context.update(locals())
        return context


@staff_member_required
def create_warehouse_order_view(request):
    form = CreateInvoiceForm(request.POST or None)
    form_title = 'Create New Invoice'
    back_url = reverse('warehouse:invoices')
    if form.is_valid():
        instance = form.save()
        return redirect(instance.get_edit_url())

    return render(request, 'dashboard/form.html', locals())


@method_decorator(staff_member_required, name='dispatch')
class UpdateWarehouseOrderView(UpdateView):
    model = Invoice
    template_name = 'warehouse/order_detail.html'
    form_class = UpdateInvoiceForm
    success_url = reverse_lazy('warehouse:invoices')

    def get_success_url(self):
        return reverse('warehouse:update_order', kwargs={'pk':self.kwargs['pk']})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        back_url = reverse('warehouse:invoices')
        if self.object.order_type in ['4', '5']:
            qs = Product.my_query.active_warehouse()
        else:
            qs = Product.my_query.active().filter(vendor=self.object.vendor)
        products_table = ProductAddTable(qs)
        instance = self.object
        images = InvoiceImage.objects.filter(order_related=self.object)
        images_table = InvoiceImageTable(images)
        RequestConfig(self.request).configure(images_table)
        RequestConfig(self.request).configure(products_table)
        context.update(locals())
        return context


@staff_member_required
def check_if_product_have_attr_view(request, pk, dk):
    product = get_object_or_404(Product, id=dk)
    instance = get_object_or_404(Invoice, id=pk)
    qs = InvoiceOrderItem.objects.filter(order=instance, product=product)
    if qs.exists():
        messages.warning(request, 'Η καταχώρηση υπάρχει ήδη.')
        return redirect(instance.get_edit_url())
    if product.have_attr:
        return redirect(reverse('warehouse:create_order_item_with_attr', kwargs={'pk': pk, 'dk': dk}))
    return redirect(reverse('warehouse:create-order-item', kwargs={'pk': pk, 'dk': dk}))


@staff_member_required
def create_order_item_with_attribute_view(request, pk, dk):
    instance = get_object_or_404(Invoice, id=pk)
    product = get_object_or_404(Product, id=dk)

    attr_qs = product.attr_class.filter(class_related__have_transcations=True)
    attr_class = attr_qs.first() if attr_qs.exists() else None
    class_attribute = attr_qs.first().class_related if attr_qs.exists() else None
    class_items = class_attribute.my_values.all()

    qs_order_item = InvoiceOrderItem.objects.filter(order=instance, product=product)

    order_item_qs = InvoiceOrderItem.objects.filter(product=product, order=instance)
    order_item = order_item_qs.first() if order_item_qs.exists() else None
    selected_data = order_item.my_attributes.all() if order_item else []
    #  form data
    form = InvoiceAttributeCreateOrEditForm(initial={'value': product.price_buy,
                                                     'discount': product.order_discount,
                                                     'measure_unit': product.measure_unit,
                                                     'order_code': product.order_code
                                                     })
    form_data = (order_item.value, order_item.discount_value) if order_item else (0, 0)
    return render(request, 'dashboard/form_with_attr.html', context=locals())


@method_decorator(staff_member_required, name='dispatch')
class CreateOrderItem(CreateView):
    model = InvoiceOrderItem
    form_class = CreateOrderItemForm
    template_name = 'dashboard/form.html'

    def get_success_url(self):
        return reverse('warehouse:update_order', kwargs={'pk': self.kwargs['pk']})

    def get_initial(self):
        self.instance = get_object_or_404(Invoice, id=self.kwargs['pk'])
        self.product = get_object_or_404(Product, id=self.kwargs['dk'])
        initial = super().get_initial()
        initial['order'] = self.instance
        initial['product'] = self.product
        initial['sku'] = self.product.order_code
        initial['value'] = self.product.price_buy
        initial['discount_value'] = self.product.order_discount
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form_title = f'Add {self.product} to {self.instance}'
        back_url, delete_url = self.get_success_url(), None
        context.update(locals())
        return context

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)


@method_decorator(staff_member_required, name='dispatch')
class UpdateInvoiceOrderItem(UpdateView):
    model = InvoiceOrderItem
    form_class = CreateOrderItemForm
    template_name = 'dashboard/form.html'

    def get_success_url(self):
        return reverse('warehouse:update_order', kwargs={'pk': self.object.order.id})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form_title = f'Edit {self.object}'
        back_url, delete_url = self.get_success_url(), reverse('warehouse:order-item-delete', kwargs={'pk': self.object.id})
        context.update(locals())
        return context


@staff_member_required
def delete_warehouse_order_item_view(request, pk):
    instance = get_object_or_404(InvoiceOrderItem, id=pk)
    instance.delete()
    return redirect(reverse('warehouse:update_order', kwargs={'pk': instance.order.id}))


@staff_member_required
def delete_warehouse_order_view(request, pk):
    instance = get_object_or_404(Invoice, id=pk)
    instance.delete()
    return redirect(reverse('warehouse:invoices'))


@staff_member_required
def create_copy_invoice_view(request, pk):
    instance = get_object_or_404(Invoice, id=pk)
    form = CopyInvoiceForm(request.POST or None)
    if form.is_valid():
        date_expired = form.cleaned_data.get('date_expired', None)
        order_type = form.cleaned_data.get('order_type', None)
        if date_expired and order_type:
            new_invoice = Invoice.objects.create(
                order_type=order_type,
                date_expired=date_expired,
                vendor=instance.vendor,
                is_paid=instance.is_paid,
                payment_method=instance.payment_method,
                taxes_modifier=instance.taxes_modifier,

            )
            for item in instance.order_items.all():
                InvoiceOrderItem.objects.create(
                    order=new_invoice,
                    product=item.product,
                    qty=item.qty,
                    value=item.value,
                    discount_value=item.discount_value
                )
            return redirect(new_invoice.get_edit_url())
    form_title, back_url = f'Αντιγραφή...', instance.get_edit_url()
    context = locals()
    return render(request, 'dashboard/form.html', context=context)


@method_decorator(staff_member_required, name='dispatch')
class VendorListView(ListView):
    model = Vendor
    template_name = 'dashboard/list_page.html'
    paginate_by = 50

    def get_queryset(self):
        queryset = Vendor.objects.all()
        queryset = Vendor.filter_data(self.request, queryset)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        queryset_table = VendorTable(self.object_list)
        create_url, back_url, page_title = reverse('warehouse:vendor_create'), reverse('dashboard:home'), 'Προμηθευτές'
        RequestConfig(self.request).configure(queryset_table)
        context.update(locals())
        return context


@method_decorator(staff_member_required, name='dispatch')
class VendorCreateView(CreateView):
    model = Vendor
    form_class = VendorForm
    template_name = 'dashboard/form.html'
    success_url = reverse_lazy('warehouse:vendors')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        back_url, delete_url = self.success_url, None
        form_title = 'Create new Vendor'
        context.update(locals())
        return context


@method_decorator(staff_member_required, name='dispatch')
class VendorUpdateView(UpdateView):
    model = Vendor
    form_class = VendorForm
    template_name = 'dashboard/form.html'
    success_url = reverse_lazy('warehouse:vendors')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        back_url, delete_url = reverse('warehouse:vendors'), reverse('warehouse:vendor_delete', kwargs={'pk': self.kwargs['pk']})
        form_title = f'Edit {self.object}'
        context.update(locals())
        return context


@staff_member_required
def delete_vendor(request, pk):
    instance = get_object_or_404(Vendor, id=pk)
    instance.delete()
    return redirect(reverse('warehouse:vendors'))


@staff_member_required
def vendor_report_view(request, pk):
    vendor = get_object_or_404(Vendor, id=pk)

    return render(request, 'warehouse/vendor_report_page.html')


@method_decorator(staff_member_required, name='dispatch')
class CreateInvoiceImageView(CreateView):
    model = InvoiceImage
    form_class = InvoiceImageForm
    template_name = 'dashboard/form.html'

    def get_success_url(self):
        return reverse('warehouse:update_order', kwargs={'pk': self.kwargs['pk']})

    def get_initial(self):
        initial = super().get_initial()
        order = get_object_or_404(Invoice, id=self.kwargs['pk'])
        initial['order_related'] = order
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form_title = 'Create new Image'
        back_url, delete_url = self.get_success_url(), None
        context.update(locals())
        return context


@method_decorator(staff_member_required, name='dispatch')
class UpdateInvoiceImageView(UpdateView):
    model = InvoiceImage
    form_class = InvoiceImageForm
    template_name = 'dashboard/form.html'

    def get_success_url(self):
        return reverse('warehouse:update_order', kwargs={'pk': self.object.order_related.id})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form_title = f'Edit {self.object}'
        back_url, delete_url = self.get_success_url(), reverse('warehouse:delete-order-image', kwargs={'pk': self.object.id})
        context.update(locals())
        return context


@staff_member_required
def delete_invoice_image_view(request, pk):
    instance = get_object_or_404(InvoiceImage, id=pk)
    instance.delete()
    return redirect(reverse('warehouse:update_order', kwargs={'pk': instance.order_related.id}))



