import django_tables2 as tables
from .models import Cart


class CartTable(tables.Table):
    action = tables.TemplateColumn('<a href="{{ record.get_edit_url }}" class="btn btn-primary">'
                                   '<i class="fa fa-edit"></> </a>', orderable=False
                                   )

    class Meta:
        template_name = 'django_tables2/bootstrap.html'
        model = Cart
        fields = ['timestamp', 'cart_id', 'shipping_method', 'payment_method', 'final_value', 'status']
