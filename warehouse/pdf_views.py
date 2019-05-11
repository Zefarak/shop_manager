from django.conf import settings
from django.http import HttpResponse, HttpResponseServerError
from django.shortcuts import get_object_or_404, render_to_response
from django.template.loader import render_to_string
from django.utils.text import slugify
from xhtml2pdf import pisa
import os
from .billing import BillInvoice, BillCategory
from .payroll import Payroll
from .tables import BillInvoiceTable, PayrollTable
from django_tables2 import RequestConfig


def link_callback(uri, rel):
    if uri.startswith(settings.MEDIA_URL):
        path = os.path.join(settings.MEDIA_ROOT,
                            uri.replace(settings.MEDIA_URL, ""))
    elif uri.startswith(settings.STATIC_URL):
        path = os.path.join(settings.STATIC_ROOT,
                            uri.replace(settings.STATIC_URL, "")
                            )
    else:
        return uri
    if not os.path.isfile(path):
        raise Exception(
            "Media URI must start with"
            f"'{settings.STATIC_URL}' or '{settings.MEDIA_URL}'"
        )
    return path


def download_cv_pdf(request, slug):
    queryset_table = ''
    if slug == 'billing':
        billing = BillInvoice.filters_data(request, BillInvoice.objects.all())
        queryset_table = BillInvoiceTable(billing)
    if slug == 'payroll':
        payroll = Payroll.filters_data(request, Payroll.objects.all())
        queryset_table = PayrollTable(payroll)
    RequestConfig(request).configure(queryset_table)
    response = HttpResponse(content_type='application/pdf')
    response["Content-Disposition"] = f"attachment; filename={slug}_report.pdf"
    html = render_to_string(template_name="pdf/base_pdf.html",
                            request=request,
                            context={
                                'queryset_table': queryset_table,
                                'title': slug
                            }
                            )
    status = pisa.CreatePDF(html,
                            dest=response,
                            link_callback=link_callback('g', 'd'))
    if status.err:
        response = HttpResponseServerError("The Pdf could not created")
    return response
