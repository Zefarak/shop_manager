import django_tables2 as tables
from .models import PaymentMethod, Store


class PaymentMethodTable(tables.Table):
    action = tables.TemplateColumn(
        "<a href='{{ record.get_edit_url }}' class='btn btn-primary btn-round'><i class='fa fa-edit'></a>",
        orderable=False,
    )

    class Meta:
        model = PaymentMethod
        template_name = 'django_tables2/bootstrap.html'
        fields = ['title', 'payment_type', 'active' ]


class StoreTable(tables.Table):
    action = tables.TemplateColumn(
        "<a href='{{ record.get_edit_url }}' class='btn btn-primary btn-round'><i class='fa fa-edit'></a>",
        orderable=False,
    )

    class Meta:
        model = PaymentMethod
        template_name = 'django_tables2/bootstrap.html'
        fields = ['title', 'active']