from django.contrib.admin.views.decorators import staff_member_required
from django.template.loader import render_to_string
from django.http import JsonResponse, HttpResponse
from django.db.models import Sum, F, Q
from .generic_expenses import GenericExpense
from .billing import BillInvoice
from site_settings.constants import CURRENCY


@staff_member_required
def report_generic_expenses_view(request):
    data = dict()
    qs = GenericExpense.filters_data(request, GenericExpense.objects.all())
    page_title = 'Γενικά Έξοδα'
    total_pay = qs.aggregate(Sum('final_value'))['final_value__sum'] if qs.exists() else 0.00
    not_paid = qs.filter(is_paid=False).aggregate(Sum('final_value'))['final_value__sum'] if\
        qs.filter(is_paid=False).exists() else 0.00
    total_pay, not_paid = f'{total_pay} {CURRENCY}', f'{not_paid} {CURRENCY}'
    data['report_result'] = render_to_string(template_name='warehouse/ajax/report_page.html',
                                             request=request,
                                             context=locals()
                                             )
    return JsonResponse(data)


@staff_member_required
def report_billing_view(request):
    data = dict()
    qs = BillInvoice.filters_data(request, GenericExpense.objects.all())
    page_title = 'Λογαριασμοί'
    total_pay = qs.aggregate(Sum('final_value'))['final_value__sum'] if qs.exists() else 0.00
    not_paid = qs.filter(is_paid=False).aggregate(Sum('final_value'))['final_value__sum'] if \
        qs.filter(is_paid=False).exists() else 0.00
    total_pay, not_paid = f'{total_pay} {CURRENCY}', f'{not_paid} {CURRENCY}'
    data['report_result'] = render_to_string(template_name='warehouse/ajax/report_page.html',
                                             request=request,
                                             context=locals()
                                             )
    return JsonResponse(data)
