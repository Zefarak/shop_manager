from django.shortcuts import get_object_or_404, HttpResponseRedirect, redirect, render
from django.urls import reverse, reverse_lazy
from django.views.generic import TemplateView, ListView, UpdateView, CreateView
from django.utils.decorators import method_decorator
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.db.models import Sum

from .models import Store, BillCategory, BillInvoice, Vendor, Invoice, Employee
from .generic_expenses import GenericExpense, GenericExpenseCategory, GenericPerson
from .tables import InvoiceTable, BillingCategoryTable, BillInvoiceTable, BillCategoryTable, GenericExpenseTable, ExpenseCategoryTable, GenericPersonTable
from site_settings.constants import CURRENCY
from .forms import BillInvoiceEditForm, BillInvoiceCreateForm, BillCategoryForm, CreateCopyForm, GenericExpenseForm, GenericExpenseCategoryForm, GenericPersonForm
from django_tables2 import RequestConfig
from dateutil.relativedelta import relativedelta
from decimal import Decimal


@method_decorator(staff_member_required, name='dispatch')
class WarehouseDashboard(TemplateView):
    template_name = 'warehouse/homepage.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        currency = CURRENCY
        invoices = Invoice.broswer.this_month_invoices()
        last_month_invoices = Invoice.broswer.last_month_invoices()
        not_paid = Invoice.broswer.not_paid()
        vendors = Vendor.objects.filter(balance__gt=0)
        queryset_table = InvoiceTable(invoices[:10])
        RequestConfig(self.request).configure(queryset_table)

        # creating strings for frontend
        this_month_value = invoices.aggregate(Sum('final_value'))['final_value__sum'] if invoices.exists() else 0.00
        last_month_invoices = last_month_invoices.aggregate(Sum('final_value'))['final_value__sum'] if last_month_invoices.exists() else 0.00
        not_paid_value = not_paid.aggregate(Sum('final_value'))['final_value__sum'] if not_paid.exists() else 0.00

        context.update(locals())
        return context


@method_decorator(staff_member_required, name='dispatch')
class TranscationHomepage(TemplateView):
    template_name = 'warehouse/transcation_homepage.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        billings = BillCategory.objects.filter(balance__gte=0)
        payroll = Employee.objects.filter(balance__gte=0)
        expenses = GenericExpense.objects.filter(is_paid=False)
        billing_dept = billings.aggregate(Sum('balance'))['balance__sum'] if billings else 0.00
        payroll_dept = payroll.aggregate(Sum('balance'))['balance__sum'] if payroll else 0.00
        expense_dept = expenses.aggregate(Sum('final_value'))['final_value__sum'] if expenses else 0.00
        total_expenses = Decimal(billing_dept)+Decimal(payroll_dept)+Decimal(expense_dept)
        currency = CURRENCY
        billings, payroll = billings[:10], payroll[:10]
        # tables
        billings = BillingCategoryTable(billings)
        RequestConfig(self.request).configure(billings)

        context.update(locals())
        return context


@method_decorator(staff_member_required, name='dispatch')
class BillingHomepageView(ListView):
    template_name = 'dashboard/list_page.html'
    model = BillInvoice
    paginate_by = 20

    def get_queryset(self):
        qs = BillInvoice.objects.all()
        qs = BillInvoice.filters_data(self.request, qs)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        stores = Store.objects.filter(active=True)
        page_title, create_url, back_url = 'Παραστατικά Λογαριασμών', reverse('warehouse:billing_invoice_create_view'),\
                                           reverse('warehouse:transcation_homepage')
        queryset_table = BillInvoiceTable(self.object_list)
        RequestConfig(self.request).configure(queryset_table)
        category_filter, search_filter, paid_filter, categories = True, True, True, BillCategory.objects.filter(active=True)

        # print
        get_params = self.request.get_full_path().split('?', 1)[1] if '?' in self.request.get_full_path() else ''
        print_button, print_url = True, reverse('warehouse:pdf_create', kwargs={'slug': 'billing'})+'?' + get_params

        #  reports
        reports, report_url = True, reverse('warehouse:report_billing')

        context.update(locals())
        return context


@method_decorator(staff_member_required, name='dispatch')
class InvoiceBillingCreateView(CreateView):
    model = BillInvoice
    template_name = 'dashboard/form.html'
    success_url = reverse_lazy('warehouse:billing_view')
    form_class = BillInvoiceCreateForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form_title, back_url = 'Δημιουργία Νέου Λογαριασμού', self.success_url
        ajax_request, ajax_title, ajax_url = True, 'Δημιουργία Λογαριασμού', reverse('warehouse:popup-new-bill')
        context.update(locals())
        return context

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)


@method_decorator(staff_member_required, name='dispatch')
class BillInvoiceEditView(UpdateView):
    model = BillInvoice
    form_class = BillInvoiceEditForm
    template_name = 'dashboard/form.html'
    success_url = reverse_lazy('warehouse:billing_view')

    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'The Invoice is Edited Correctly')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # instance = get_object_or_404(BillInvoice, id=pk)
        form_title = f'Επεξεργασία {self.object.title}'
        back_url, delete_url = self.get_success_url, self.object.get_delete_url()
        copy_url, button_url = reverse('warehouse:bill-copy', kwargs={'pk': self.object.id, 'date_range': 'month'}), True
        context.update(locals())
        return context


@staff_member_required
def quick_billing_pay(request, pk):
    instance = get_object_or_404(BillInvoice, id=pk)
    instance.is_paid = True
    instance.save()
    messages.success(request, f'The Invoice {instance.title} is paid.')
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@staff_member_required
def create_bill_copy(request, pk, date_range):
    instance = get_object_or_404(BillInvoice, id=pk)
    new_date = instance.date_expired + relativedelta(months=1) if date_range == 'month' \
        else instance.date_expired + relativedelta(days=7) if date_range == 'week' else instance.date_expired \
                                                                                        + relativedelta(days=7)
    instance.pk = None
    instance.date_expired = new_date
    instance.is_paid = False
    instance.save()
    return redirect(instance.get_edit_url())


@method_decorator(staff_member_required, name='dispatch')
class CreateBillingInvoiceView(CreateView):
    model = BillInvoice
    template_name = 'warehouse/form.html'
    form_class = BillInvoiceCreateForm

    def get_form(self, *args, **kwargs):
        self.store = get_object_or_404(Store, id=self.kwargs['pk'])
        form = super().get_form(*args, **kwargs)
        form.fields['category'].queryset = BillCategory.objects.filter(store=self.store, active=True)
        return form

    def get_success_url(self):
        self.store = get_object_or_404(Store, id=self.kwargs['pk'])
        return reverse('warehouse:billing_store_view', kwargs={'pk': self.store.id})

    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'The Invoice is Created.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form_title = f'Add new bill to {self.store.title}'
        back_url, delete_url = self.get_success_url(), None
        context.update(locals())
        return context


@staff_member_required
def delete_bill_invoice_view(request, pk):
    instance = get_object_or_404(BillInvoice, id=pk)
    instance.delete()
    return redirect(reverse('warehouse:billing_store_view', kwargs={'pk': instance.category.store.id}))


@method_decorator(staff_member_required, name='dispatch')
class BillCategoryListView(ListView):
    model = BillCategory
    template_name = 'dashboard/list_page.html'
    paginate_by = 20

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        page_title, back_url, create_url = 'Λογαριασμοί', reverse('warehouse:dashboard'),\
                                           reverse('warehouse:billing_category_create_view')
        queryset_table = BillCategoryTable(self.object_list)
        RequestConfig(self.request).configure(queryset_table)
        # filters
        context.update(locals())
        return context


@method_decorator(staff_member_required, name='dispatch')
class CreateBillingCategoryView(CreateView):
    model = BillCategory
    template_name = 'dashboard/form.html'
    form_class = BillCategoryForm
    success_url = reverse_lazy('warehouse:billing_category_view')

    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'The Bill is created')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form_title = 'Create new Bill'
        back_url = self.get_success_url
        context.update(locals())
        return context


@method_decorator(staff_member_required, name='dispatch')
class EditBillingCategoryView(UpdateView):
    model = BillCategory
    template_name = 'dashboard/form.html'
    form_class = BillCategoryForm

    def get_success_url(self):
        self.my_obj = get_object_or_404(BillCategory, id=self.kwargs['pk'])
        return reverse('warehouse:billing_store_view', kwargs={'pk': self.my_obj.store.id})

    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'The Bill is created')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form_title = f'Edit {self.object}',
        back_url, delete_url = self.get_success_url(),\
                               reverse('warehouse:bill_category_delete_view', kwargs={'pk': self.kwargs['pk']})
        context.update(locals())
        return context


@staff_member_required
def delete_bill_category_view(request, pk):
    instance = get_object_or_404(BillCategory, id=pk)
    if not instance.bills.exists():
        instance.delete()
    else:
        messages.warning(request, 'You cant delete this.')
    return redirect(reverse('warehouse:billing_store_view', kwargs={'pk': instance.store.id}))


@staff_member_required
def billing_create_copy(request, pk):
    instance = get_object_or_404(BillInvoice, id=pk)
    form_title = 'Create Copy'
    back_url = reverse('warehouse:bill_invoice_edit_view', kwargs={'pk': instance.id})
    form = CreateCopyForm(request.POST or None)
    if form.is_valid():
        days = form.changed_data.get('days', 1)
        months = form.cleaned_data.get('months', None)
        repeat = form.cleaned_data.get('repeat', 1)
        print(days, months, repeat)
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    context = locals()
    return render(request, 'dashboard/form.html')


@method_decorator(staff_member_required, name='dispatch')
class GenericExpenseListView(ListView):
    template_name = 'dashboard/list_page.html'
    model = GenericExpense
    paginate_by = 50

    def get_queryset(self):
        qs = GenericExpense.objects.all()
        qs = GenericExpense.filters_data(self.request, qs)
        return qs

    def get_context_data(self, **kwargs):
        context = super(GenericExpenseListView, self).get_context_data(**kwargs)
        page_title, back_url, create_url = ['Γενικά Έξοδα', reverse('warehouse:transcation_homepage'),
                                            reverse('warehouse:generic-expense-create')]
        queryset_table = GenericExpenseTable(self.object_list)
        RequestConfig(self.request).configure(queryset_table)
        search_filter, category_filter, employee_filter, date_filter, paid_filter = [True]*5
        categories, employees = [GenericExpenseCategory.objects.filter(active=True),
                                 GenericPerson.objects.filter(active=True)]

        # reports
        get_params = self.request.get_full_path().split('?', 1)[1] if '?' in self.request.get_full_path() else ''
        reports, report_url = True, reverse('warehouse:report_generic_expenses') + '?' + get_params

        #  print
        report_button, report_url =[True, reverse('warehouse:pdf_create', kwargs={'slug': 'generic-expense'})
                                    + '?' + get_params]

        context.update(locals())
        return context


@method_decorator(staff_member_required, name='dispatch')
class GenericExpenseCreateView(CreateView):
    template_name = 'dashboard/form.html'
    model = GenericExpense
    form_class = GenericExpenseForm
    success_url = reverse_lazy('warehouse:generic-expense-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form_title, back_url = 'Δημιουργία Εξόδου', self.success_url
        ajax_request, ajax_title, ajax_url = True, 'Δημιουργία Νέας Εταιρίας', reverse('warehouse:popup-generic-person')
        context.update(locals())
        return context


@method_decorator(staff_member_required, name='dispatch')
class GenericExpenseUpdateView(UpdateView):
    model = GenericExpense
    template_name = 'dashboard/form.html'
    success_url = reverse_lazy('warehouse:generic-expense-list')
    form_class = GenericExpenseForm

    def get_context_data(self, **kwargs):
        context = super(GenericExpenseUpdateView, self).get_context_data(**kwargs)
        self.old_person = self.object.person
        form_title, back_url, delete_url = 'Δημιουργία Εξόδου', self.success_url, self.object.get_delete_url()
        ajax_request, ajax_title, ajax_url = True, 'Δημιουργία Νέας Εταιρίας', reverse('warehouse:popup-generic-person')
        context.update(locals())
        return context

    def form_valid(self, form):
        old_instance = get_object_or_404(GenericExpense, id=self.kwargs['pk'])
        form.save()
        changed_data = form.cleaned_data
        if 'person' in changed_data:
            old_instance.person.save()
        if 'category' in changed_data:
            old_instance.category.save()
        messages.success(self.request, 'Το παραστατικό επεξεργάστηκε')
        return super(GenericExpenseUpdateView, self).form_valid(form)


@staff_member_required
def delete_generic_expense(request, pk):
    instance = get_object_or_404(GenericExpense, id=pk)
    instance.delete()
    return redirect(reverse('warehouse:generic-expense-list'))


@method_decorator(staff_member_required, name='dispatch')
class GenericExpenseCateListView(ListView):
    template_name = 'dashboard/list_page.html'
    model = GenericExpenseCategory
    paginate_by = 50

    def get_queryset(self):
        qs = GenericExpenseCategory.objects.all()
        qs = GenericExpenseCategory.filters_data(self.request, qs)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        page_title, back_url, create_url = ['Κατηγορίες Εξόδων', reverse('warehouse:transcation_homepage'),
                                            reverse('warehouse:generic-expense-cate-create')]
        queryset_table = ExpenseCategoryTable(self.object_list)
        RequestConfig(self.request).configure(queryset_table)
        search_filter, active_filter = True, True
        context.update(locals())
        return context


@method_decorator(staff_member_required, name='dispatch')
class GenericExpenseCateCreateView(CreateView):
    template_name = 'dashboard/form.html'
    model = GenericExpenseCategory
    form_class = GenericExpenseCategoryForm
    success_url = reverse_lazy('warehouse:generic-expense-cate-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form_title, back_url = 'Δημιουργία Εξόδου', self.success_url
        context.update(locals())
        return context

    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'Η κατηγορία δημιουργήθηκε')
        return super().form_valid(form)


@method_decorator(staff_member_required, name='dispatch')
class GenericExpenseCateUpdateView(UpdateView):
    model = GenericExpenseCategory
    template_name = 'dashboard/form.html'
    success_url = reverse_lazy('warehouse:generic-expense-cate-list')
    form_class = GenericExpenseCategoryForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form_title, back_url, delete_url = [f'Επεξεργασία {self.object.title}',self.success_url, self.object.get_delete_url()]
        context.update(locals())
        return context

    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'Η επεξεργασία αποθηκεύτηκε')
        return super().form_valid(form)


@staff_member_required
def delete_generic_expense_category(request, pk):
    instance = get_object_or_404(GenericExpenseCategory, id=pk)
    instance.delete()
    return redirect(reverse('warehouse:generic-expense-cate-list'))


@method_decorator(staff_member_required, name='dispatch')
class GenericExpensePersonListView(ListView):
    template_name = 'dashboard/list_page.html'
    model = GenericPerson
    paginate_by = 50

    def get_queryset(self):
        qs = GenericPerson.objects.all()
        qs = GenericPerson.filters_data(self.request, qs)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        page_title, back_url, create_url = ['Εταιρίες/Ιδιώτες', reverse('warehouse:transcation_homepage'),
                                            reverse('warehouse:generic-expense-person-create')]
        queryset_table = GenericPersonTable(self.object_list)
        RequestConfig(self.request).configure(queryset_table)
        search_filter, active_filter = True, True
        context.update(locals())
        return context


@method_decorator(staff_member_required, name='dispatch')
class GenericExpensePersonCreateView(CreateView):
    template_name = 'dashboard/form.html'
    model = GenericPerson
    form_class = GenericPersonForm
    success_url = reverse_lazy('warehouse:generic-expense-person-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form_title, back_url = 'Δημιουργία', self.success_url
        context.update(locals())
        return context

    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'Η κατηγορία δημιουργήθηκε')
        return super().form_valid(form)


@method_decorator(staff_member_required, name='dispatch')
class GenericExpensePersonUpdateView(UpdateView):
    model = GenericPerson
    template_name = 'dashboard/form.html'
    success_url = reverse_lazy('warehouse:generic-expense-person-list')
    form_class = GenericPersonForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form_title, back_url, delete_url = f'Επεξεργασια {self.object.title}', self.success_url, self.object.get_delete_url()
        context.update(locals())
        return context

    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'Η επεξεργασία ολοκληρώθηκε')
        return super().form_valid(form)


@staff_member_required
def delete_generic_expense_person(request, pk):
    instance = get_object_or_404(GenericPerson, id=pk)
    instance.delete()
    return redirect(reverse('warehouse:generic-expense-person-list'))
