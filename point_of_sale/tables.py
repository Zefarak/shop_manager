from django.utils.html import format_html
import django_tables2 as tables

from accounts.models import Profile
from .models import Order, OrderItem


class ProfileTable(tables.Table):
    action = tables.TemplateColumn("<a href='{{ record.get_edit_url }}' class='btn btn-primary'><i class='fa fa-edit'>"
                                   "</i> </a>", orderable=False, verbose_name='Επεξεργασία'
                                   )
    tag_balance = tables.Column(orderable=False, verbose_name='Υπόλοιπο')
    pay = tables.TemplateColumn("<a href='{% url 'point_of_sale:costumer_pay' record.id %}' class='btn btn-success'>"
                                "Πληρωμή</a> ", orderable=False, verbose_name='Γρήγορη Πληρωμή')
    card_ = tables.TemplateColumn("<a href='{{ record.get_card_url }}' class='btn btn-info btn-round'>"
                                "Καρτέλα</a> ", orderable=False, verbose_name='Καρτέλες')

    class Meta:
        model = Profile
        template_name = 'django_tables2/bootstrap.html'
        fields = ['first_name', 'last_name', 'notes', 'cellphone', 'tag_balance']


class OrderTable(tables.Table):
    action = tables.TemplateColumn("<a href='{{ record.get_edit_url }}' class='btn btn-primary'>Edit</a>", orderable=False)
    tag_final_value = tables.Column(orderable=False, verbose_name='Value')

    class Meta:
        model = Order
        template_name = 'django_tables2/bootstrap.html'
        fields = ['date_expired', 'title', 'order_type', 'profile', 'status', 'tag_final_value']


class OrderItemListTable(tables.Table):
    get_date = tables.Column(orderable=False, verbose_name='Ημερομηνία')

    class Meta:
        model = OrderItem
        template_name = 'django_tables2/bootstrap.html'
        fields = ['get_date', 'title', 'qty', 'tag_final_value', 'tag_total_value']
