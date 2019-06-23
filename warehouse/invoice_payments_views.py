from django.shortcuts import get_object_or_404, HttpResponseRedirect, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import TemplateView, ListView, UpdateView, CreateView
from django.utils.decorators import method_decorator
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.db.models import Sum

from .forms import VendorPaycheckInvoiceForm, PaycheckVendorForm
from .models import VendorPaycheck, Invoice, Vendor
from .tables import VendorPaycheckInvoiceTable, VendorPaycheckTable
from site_settings.models import Store
from site_settings.tools import list_view_table
from django_tables2 import RequestConfig


@method_decorator(staff_member_required, name='dispatch')
class InvoicePaymentListView(ListView):
    model = VendorPaycheck
    template_name = 'dashboard/list_page.html'

    def get_queryset(self):
        instance = get_object_or_404(Invoice, id=self.kwargs['pk'])
        qs = VendorPaycheck.objects.filter(order_related=instance)
        return qs

    def get_context_data(self, *args,  **kwargs):
        context = super().get_context_data(**kwargs)
        queryset_table = VendorPaycheckInvoiceTable(self.object_list)
        RequestConfig(self.request).configure(queryset_table)
        paid_filter = [True]

        instance = get_object_or_404(Invoice, id=self.kwargs['pk'])
        create_url, back_url = [reverse('warehouse:invoice_paycheck_create', kwargs={'pk': instance.id}),
                                instance.get_edit_url()
                                ]
        page_title = f'Πληρωμές - {instance.title}- Συνολικό Πληρωτέο Ποσό - {instance.tag_paid_value()},' \
                     f' Υπόλοιπο ==> {instance.tag_not_paid_value()}'
        context = locals()
        return context


class InvoicePaymentCreateView(CreateView):
    model = VendorPaycheck
    form_class = VendorPaycheckInvoiceForm
    template_name = 'dashboard/form.html'

    def get_success_url(self):
        instance = get_object_or_404(Invoice, id=self.kwargs['pk'])
        return instance.get_payment_url()

    def get_initial(self):
        initial = super().get_initial()
        invoice = get_object_or_404(Invoice, id=self.kwargs['pk'])

        initial['order_related'] = invoice
        initial['vendor'] = invoice.vendor
        initial['payment_method'] = invoice.payment_method
        initial['value'] = invoice.final_value
        initial['title'] = f'Πληρωμή - {invoice.title}'
        initial['date_expired'] = invoice.date_expired
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        instance = get_object_or_404(Invoice, id=self.kwargs['pk'])
        back_url, form_title = instance.get_edit_url(), f'Πληρωμή Παραστατικου - {instance.title}'
        context.update(locals())
        return context

    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'Η πληρώμη καταχωρήθηκε.')
        return super().form_valid(form)


@method_decorator(staff_member_required, name='dispatch')
class InvoicePaymentUpdateView(UpdateView):
    model = VendorPaycheck
    form_class = VendorPaycheckInvoiceForm
    template_name = 'dashboard/form.html'

    def get_success_url(self):
        return reverse('warehouse:invoice_paycheck_list', kwargs={'pk': self.object.order_related})

    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'H Πληρωμή ανανεώθηκε')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form_title, back_url = f'{self.object.title}', self.get_success_url()

        context.update(locals())
        return context

@method_decorator(staff_member_required, name='dispatch')
class PayCheckListView(ListView):
    model = VendorPaycheck
    template_name = 'dashboard/list_page.html'
    paginate_by = 50

    def get_queryset(self):
        queryset = VendorPaycheck.filters_data(self.request, VendorPaycheck.objects.all())
        return queryset

    def get_context_data(self,  **kwargs):
        context = super().get_context_data(**kwargs)
        vendors = Vendor.objects.filter(active=True)
        page_title, back_url, create_url = 'Επιταγές', reverse('warehouse:dashboard'), reverse('warehouse:paycheck_create')
        queryset_table = VendorPaycheckTable(self.object_list)
        RequestConfig(self.request).configure(queryset_table)
        search_filter, vendor_filter, paid_filter = [True]*3
        vendors = Vendor.objects.filter(active=True)
        context.update(locals())
        return context


@method_decorator(staff_member_required, name='dispatch')
class PaycheckDetailView(UpdateView):
    model = VendorPaycheck
    form_class = PaycheckVendorForm
    template_name = 'dashboard/form.html'
    success_url = reverse_lazy('warehouse:paychecks')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form_title = f'Επεξεργασία {self.object}'
        back_url, delete_url = self.success_url, self.object.get_delete_url
        context.update(locals())
        return context

    def form_valid(self, form):
        form.save()

        return super().form_valid(form)


@method_decorator(staff_member_required, name='dispatch')
class PaycheckCreateView(CreateView):
    model = VendorPaycheck
    form_class = PaycheckVendorForm
    template_name = 'dashboard/form.html'
    success_url = reverse_lazy('warehouse:paychecks')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form_title = 'Δημιουργία Νέας Πληρωμής'
        back_url, delete_url = self.success_url, None
        context.update(locals())
        return context

    def form_valid(self, form):
        form.save()

        return super().form_valid(form)


@staff_member_required
def delete_paycheck(request, pk):
    instance = get_object_or_404(VendorPaycheck, id=pk)
    instance.delete()

    return redirect('warehouse:paychecks')
