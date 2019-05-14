from django.shortcuts import get_object_or_404, HttpResponseRedirect, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import TemplateView, ListView, UpdateView, CreateView
from django.utils.decorators import method_decorator
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.db.models import Sum

from .payroll import Payroll, Employee, Occupation, PAYROLL_CHOICES
from .forms import EmployeeForm, OccupationForm, PayrollForm
from .tables import PayrollTable, EmployeeTable, OccupationTable
from site_settings.models import Store
from site_settings.tools import list_view_table
from django_tables2 import RequestConfig


@method_decorator(staff_member_required, name='dispatch')
class PayrollListView(ListView):
    template_name = 'dashboard/list_page.html'
    model = Payroll
    paginate_by = 20

    def get_queryset(self):
        qs = Payroll.objects.all()
        qs = Payroll.filters_data(self.request, qs)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        create_url, back_url, page_title = reverse('warehouse:payroll_create'), reverse('warehouse:dashboard'), 'Μισθοδοσία'
        queryset_table = PayrollTable(self.object_list)
        RequestConfig(self.request).configure(queryset_table)

        #  filters
        employee_filter, search_filter, paid_filter, date_filter = True, True, True, True
        employees = Employee.objects.filter(active=True)

        # pdf creator
        get_params = self.request.get_full_path().split('?', 1)[1] if '?' in self.request.get_full_path() else ''
        report_button, report_url = True, reverse('warehouse:pdf_create', kwargs={'slug': 'payroll'})+'?' + get_params

        context.update(locals())
        return context


@method_decorator(staff_member_required, name='dispatch')
class PayrollCreateView(CreateView):
    model = Payroll
    form_class = PayrollForm
    template_name = 'dashboard/form.html'
    success_url = reverse_lazy('warehouse:payroll_homepage')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form_title, back_url = f'Δημιουργία Μισθοδοσίας', self.success_url

        ajax_request, ajax_url, ajax_title = True, reverse('warehouse:popup-employee'), 'Υπάλληλος'
        context.update(locals())
        return context

    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'New payroll Added')
        return super().form_valid(form)


@method_decorator(staff_member_required, name='dispatch')
class PayrollUpdateView(UpdateView):
    model = Payroll
    form_class = PayrollForm
    template_name = 'dashboard/form.html'
    success_url = reverse_lazy('warehouse:payroll_homepage')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form_title = f'Edit Payroll {self.object.title}'
        back_url, delete_url = self.success_url, reverse('warehouse:payroll_delete', kwargs={'pk': self.object.id})
        ajax_request, ajax_url, ajax_title = True, reverse('warehouse:popup-employee'), 'Υπάλληλος'
        context.update(locals())
        return context

    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'Payroll is Edit')
        return super().form_valid(form)


@staff_member_required
def delete_payroll(request, pk):
    instance = get_object_or_404(Payroll, id=pk)
    instance.delete()
    messages.success(request, 'The Payroll is deleted')
    return redirect(reverse('warehouse:employee-card-detail', kwargs={'pk': instance.employee.id}))


@method_decorator(staff_member_required, name='dispatch')
class EmployeeListView(ListView):
    model = Employee
    template_name = 'dashboard/list_page.html'

    def get_queryset(self):
        queryset = Employee.objects.all()
        queryset = Employee.filters_data(self.request, queryset)
        return queryset

    def get_context_data(self,**kwargs):
        context = super(EmployeeListView, self).get_context_data(**kwargs)
        page_title, create_url, back_url = 'Υπάλληλοι', reverse('warehouse:payroll_employee_create'), \
                                           reverse('warehouse:transcation_homepage')
        queryset_table = EmployeeTable(self.object_list)
        RequestConfig(self.request).configure(queryset_table)

        store_filter, occupation_filter = True, True
        stores, occupations = Store.objects.filter(active=True), Occupation.objects.filter(active=True)

        context.update(locals())
        return context


@method_decorator(staff_member_required, name='dispatch')
class EmployeeCreateView(CreateView):
    model = Employee
    form_class = EmployeeForm
    template_name = 'dashboard/form.html'
    success_url = reverse_lazy('warehouse:payroll_employee')

    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'New Employee Created')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form_title = 'Δημιουργία Νέου Υπαλλήλου'
        back_url, delete_url = self.success_url, None

        # popup
        ajax_request, ajax_url, ajax_title = True, reverse('warehouse:popup-occupation'), 'Επάγγελμα'
        context.update(locals())
        return context


@method_decorator(staff_member_required, name='dispatch')
class EmployeeEditView(UpdateView):
    model = Employee
    form_class = EmployeeForm
    template_name = 'dashboard/form.html'
    success_url = reverse_lazy('warehouse:payroll_employee')

    def form_valid(self, form):
        form.save()
        messages.success(self.request, f'{self.object.title} Edited Corectly')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        for_title = f'Edit {self.object.title}'
        back_url, delete_url = self.success_url, self.object.get_delete_url()

        # popup
        ajax_request, ajax_url, ajax_title = True, reverse('warehouse:popup-occupation'), 'Επάγγελμα'
        context.update(locals())
        return context


@staff_member_required
def delete_employee(request, pk):
    instance = get_object_or_404(Employee, id=pk)
    if instance.person_invoices.exists():
        messages.warning(request, 'You cant delete this employee')
    else:
        instance.delete()
    return redirect(reverse('warehouse:payroll_employee'))


@method_decorator(staff_member_required, name='dispatch')
class OccupationListView(ListView):
    model = Occupation
    template_name = 'dashboard/list_page.html'

    def get_queryset(self):
        queryset = Occupation.objects.all()
        queryset = Occupation.filters_data(self.request, queryset)
        return queryset

    def get_context_data(self, **kwargs):
        context = super(OccupationListView, self).get_context_data(**kwargs)
        data = {'store': Store.objects.all()}
        filters = ['search_filter', 'store_filter']
        page_title, back_url, create_url = 'Επαγγέλματα', reverse('warehouse:transcation_homepage'),\
                                           reverse('warehouse:occupation_create')
        list_view_table(self.request, context, OccupationTable(self.object_list), filters, data)
        context.update(locals())
        return context


@method_decorator(staff_member_required, name='dispatch')
class OccupationCreateView(CreateView):
    model = Occupation
    form_class = OccupationForm
    template_name = 'dashboard/form.html'
    success_url = reverse_lazy('warehouse:occupation_list')

    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'New Occupation is saved')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form_title = 'Create New Occupation'
        back_url, delete_url = self.success_url, None
        context.update(locals())
        return context


@method_decorator(staff_member_required, name='dispatch')
class OccupationUpdateView(UpdateView):
    model = Occupation
    form_class = OccupationForm
    template_name = 'dashboard/form.html'
    success_url = reverse_lazy('warehouse:occupation_list')

    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'The Occupation is saved')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form_title = f'Edit {self.object.title}'
        back_url, delete_url = self.success_url, reverse('warehouse:occupation_delete', kwargs={'pk': self.object.id})
        context.update(locals())
        return context


@staff_member_required
def delete_occupation(request, pk):
    instance = get_object_or_404(Occupation, id=pk)
    instance.delete()
    return redirect(reverse('warehouse:occupation_list'))


@staff_member_required
def payroll_quick_pay(request, pk):
    instance = get_object_or_404(Payroll, id=pk)
    instance.is_paid = True
    instance.save()
    messages.success(request, 'The payroll is Paid')
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


