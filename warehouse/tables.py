import django_tables2 as tables
from django.utils.html import format_html
from .models import InvoiceImage
from catalogue.product_details import VendorPaycheck
from .models import Invoice, Vendor
from .billing import BillCategory, BillInvoice
from .payroll import Employee, Payroll, Occupation
from .billing import BillCategory
from .generic_expenses import GenericExpense, GenericExpenseCategory, GenericPerson
from catalogue.models import Product


class ImageColumn(tables.Column):
    def render(self, value):
        return format_html('<img class="img-thumbnail" style="width:100px;height:100px" src="/media/{}" />', value)


class InvoiceImageTable(tables.Table):
    file = ImageColumn()
    edit_button = tables.TemplateColumn("<a href='{{ record.get_edit_url }}' class='btn btn-primary'>Edit</a>")

    class Meta:
        model = InvoiceImage
        fields = ['id', 'file']
        template_name = 'django_tables2/bootstrap.html'


class PaycheckTable(tables.Table):
    action = tables.TemplateColumn("<a href='{{ record.get_edit_url }}' class='btn btn-primary'><i class='far fa-edit'>"
                                   "</i></a>",
                                    orderable=False,
                                    )

    class Meta:
        model = VendorPaycheck
        fields = ['date_expired', 'vendor', 'payment_method', 'value', 'is_paid']
        template_name = 'django_tables2/bootstrap.html'


class InvoiceTable(tables.Table):
    action = tables.TemplateColumn("<a href='{{ record.get_edit_url }}' class='btn btn-primary'>Edit</a>",
                                   orderable=False,
                                   )
    tag_clean_value = tables.Column(orderable=False, verbose_name='Clean Value')
    tag_final_value = tables.Column(orderable=False, verbose_name='Value')

    class Meta:
        model = Invoice
        fields = ['id', 'date_expired', 'title', 'order_type', 'vendor', 'tag_clean_value', 'tag_final_value']
        template_name = 'django_tables2/bootstrap.html'


class VendorTable(tables.Table):
    action = tables.TemplateColumn("<a href='{{ record.get_edit_url }}' class='btn btn-primary btn-round'>Επεξεργασία</a>",
                                   orderable=False,
                                   )
    tag_balance = tables.Column(orderable=False)

    class Meta:
        model = Vendor
        template_name = 'django_tables2/bootstrap.html'
        fields = ['id', 'title', 'phone', 'tag_balance']


class ProductAddTable(tables.Table):
    action = tables.TemplateColumn('<a href="{% url "warehouse:order_item_check" instance.id record.id %}" '
                                   'class="btn btn-primary">Add</a>', orderable=False)

    class Meta:
        model = Invoice
        fields = ['order_code', 'title', 'price_buy', 'qty']
        template_name = 'django_tables2/bootstrap.html'


class BillingCategoryTable(tables.Table):
    action = tables.TemplateColumn(
        "<a href='{{ record.get_edit_url }}' class='btn btn-primary btn-round'><i class='fa fa-edit'></a>",
        orderable=False,
        )
    tag_balance = tables.Column(orderable=False)

    class Meta:
        model = BillCategory
        fields = ['title', 'tag_balance']
        template_name = 'django_tables2/bootstrap.html'


class BillInvoiceTable(tables.Table):
    action = tables.TemplateColumn(
        "<a href='{{ record.get_edit_url }}' class='btn btn-primary btn-round'><i class='fa fa-edit'></a>",
        orderable=False,
    )

    class Meta:
        attrs = {'class': 'table'}
        model = BillInvoice
        template_name = 'django_tables2/bootstrap.html'
        fields = ['date_expired', 'title', 'category', 'tag_final_value', 'is_paid']


class BillCategoryTable(tables.Table):
    action = tables.TemplateColumn(
        "<a href='{{ record.get_edit_url }}' class='btn btn-primary btn-round'><i class='fa fa-edit'></a>",
        orderable=False,
    )
    tag_balance = tables.Column(orderable=False)

    class Meta:
        model = BillCategory
        template_name = 'django_tables2/bootstrap.html'
        fields = ['title', 'store', 'tag_balance']


class PayrollTable(tables.Table):
    action = tables.TemplateColumn(
        "<a href='{{ record.get_edit_url }}' class='btn btn-primary btn-round'><i class='fa fa-edit'></a>",
        orderable=False,
    )
    tag_final_value = tables.Column(orderable=False)

    class Meta:
        model = BillCategory
        template_name = 'django_tables2/bootstrap.html'
        fields = ['date_expired', 'title', 'person', 'payment_method', 'is_paid', 'tag_final_value']


class EmployeeTable(tables.Table):
    action = tables.TemplateColumn(
        "<a href='{{ record.get_edit_url }}' class='btn btn-primary btn-round'><i class='fa fa-edit'></a>",
        orderable=False,
    )
    tag_balance = tables.Column(orderable=False)

    class Meta:
        model = Employee
        template_name = 'django_tables2/bootstrap.html'
        fields = ['title', 'occupation', 'store', 'tag_balance', 'active']


class OccupationTable(tables.Table):
    action = tables.TemplateColumn(
        "<a href='{{ record.get_edit_url }}' class='btn btn-primary btn-round'><i class='fa fa-edit'></a>",
        orderable=False,
    )

    class Meta:
        model = Occupation
        template_name = 'django_tables2/bootstrap.html'
        fields = ['title', 'store', 'active']


class GenericExpenseTable(tables.Table):
    tag_final_value = tables.Column(orderable=False, verbose_name='Αξία')
    action = tables.TemplateColumn(
        "<a href='{{ record.get_edit_url }}' class='btn btn-primary btn-round'><i class='fa fa-edit'></a>",
        orderable=False,
    )

    class Meta:
        model = GenericExpense
        template_name = 'django_tables2/bootstrap.html'
        fields = ['title', 'category', 'person', 'is_paid']


class ExpenseCategoryTable(tables.Table):
    action = tables.TemplateColumn(
        "<a href='{{ record.get_edit_url }}' class='btn btn-primary btn-round'><i class='fa fa-edit'></a>",
        orderable=False,
    )
    tag_balance = tables.Column(orderable=False, verbose_name='Υπόλοιπο')

    class Meta:
        model = GenericExpenseCategory
        template_name = 'django_tables2/bootstrap.html'
        fields = ['title', 'tag_balance', 'active']


class GenericPersonTable(tables.Table):
    action = tables.TemplateColumn(
        "<a href='{{ record.get_edit_url }}' class='btn btn-primary btn-round'><i class='fa fa-edit'></a>",
        orderable=False,
    )

    class Meta:
        model = GenericPerson
        template_name = 'django_tables2/bootstrap.html'
        fields = ['title', 'phone', 'tag_balance', 'active']
