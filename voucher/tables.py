import django_tables2 as tables
from .models import Voucher


class VoucherTable(tables.Table):
    action = tables.TemplateColumn("<a href='{{ record.get_edit_url }}' class='btn btn-primary btn-round'>"
                                   "<i class='fa fa-edit'> </i></a>",
                                   orderable=False
                                   )

    class Meta:
        model = Voucher
        fields = ['name', 'code', 'usage', 'start_date', 'end_date', 'active', 'action']
        template_name = 'django_tables2/bootstrap.html'