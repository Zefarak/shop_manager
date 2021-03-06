import django_tables2 as tables
from django.utils.html import format_html
from .models import InvoiceImage

from .models import Invoice, Vendor, InvoiceAttributeItem, InvoiceOrderItem, VendorPaycheck
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


class InvoiceTable(tables.Table):
    action = tables.TemplateColumn("<a href='{{ record.get_edit_url }}' class='btn btn-primary'>"
                                   "<i class='fa fa-edit'></i></a>",
                                   orderable=False,
                                   )
    test_button = tables.TemplateColumn('''
        <div class="dropdown">
  <button class="btn btn-secondary dropdown-toggle" type="button" id="dropdownMenuButton_{{ record.id }}" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
    Επιλογές
  </button>
  <div class="dropdown-menu" aria-labelledby="dropdownMenuButton_{{ record_id }}">
    <a class="dropdown-item" href="{{ record.get_print_url }}">Εκτύπωση</a>
    <a class="dropdown-item" href="{{ record.get_copy_url }}">Αντίγραφο</a>
    <a onclick="return confirm("Είσαι σίγουρος;")" class="dropdown-item" href="{{ record.get_delete_url }}">Διαγραφή</a>
  </div>
</div>
    ''')
    tag_clean_value = tables.Column(orderable=False, verbose_name='Καθαρή Αξία')
    tag_final_value = tables.Column(orderable=False, verbose_name='Τελική Αξία')

    class Meta:
        model = Invoice
        fields = ['id', 'date_expired', 'title', 'order_type', 'vendor', 'is_paid', 'tag_clean_value', 'tag_final_value']
        template_name = 'django_tables2/bootstrap.html'


class VendorTable(tables.Table):
    action = tables.TemplateColumn("<a href='{{ record.get_edit_url }}' class='btn btn-primary btn-round'><i class='fa fa-edit'></i></a>",
                                   orderable=False,
                                   )
    report = tables.TemplateColumn("<a href='{{ record.get_report_url }}' class='btn btn-success btn-round'>Καρτέλα</a>",
                                   orderable=False,
                                   )
    tag_balance = tables.Column(orderable=False, verbose_name='Υπόλοιπο')

    class Meta:
        model = Vendor
        template_name = 'django_tables2/bootstrap.html'
        fields = ['id', 'title', 'phone', 'tag_balance', 'report']


class ProductAddTable(tables.Table):
    action = tables.TemplateColumn('<a href="{% url "warehouse:order_item_check" instance.id record.id %}" '
                                   'class="btn btn-success"><i class="fa fa-plus"></i></a>', orderable=False)

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


class InvoiceAttributeItemTable(tables.Table):
    action = tables.TemplateColumn(
        "<a href='{{ record.get_edit_url }}' class='btn btn-primary btn-round'><i class='fa fa-edit'></a>",
        orderable=False,
    )

    class Meta:
        model = InvoiceAttributeItem
        template_name = 'django_tables2/bootstrap.html'
        fields = ['attribute_related', ]


class HomepageInvoiceOrderItemTable(tables.Table):
    action = tables.TemplateColumn(
        "<a href='{{ record.get_edit_url }}' class='btn btn-primary btn-round'><i class='fa fa-edit'></a>",
        orderable=False,
    )

    class Meta:
        model = InvoiceOrderItem
        template_name = 'django_tables2/bootstrap.html'
        fields = ['qty',]


class HomepageInvoiceTable(tables.Table):
    action = tables.TemplateColumn(
        "<a href='{{ record.get_edit_url }}' class='btn btn-primary btn-round'><i class='fa fa-edit'></a>",
        orderable=False,
    )

    class Meta:
        model = Invoice
        template_name = 'django_tables2/bootstrap.html'
        fields = ['date_expired', 'vendor', 'title', 'tag_final_value']


class VendorPaycheckInvoiceTable(tables.Table):
    action = tables.TemplateColumn(
        "<a href='{{ record.get_invoice_edit_url }}' class='btn btn-primary btn-round'><i class='fa fa-edit'></a>",
        orderable=False,
    )

    class Meta:
        model = VendorPaycheck
        template_name = 'django_tables2/bootstrap.html'
        fields = ['date_expired', 'title', 'payment_method', 'tag_value', 'is_paid']


class VendorPaycheckTable(tables.Table):
    action = tables.TemplateColumn(
        "<a href='{{ record.get_edit_url }}' class='btn btn-primary btn-round'><i class='fa fa-edit'></a>",
        orderable=False,
    )
    tag_value = tables.Column(verbose_name='Αξία')

    class Meta:
        model = VendorPaycheck
        template_name = 'django_tables2/bootstrap.html'
        fields = ['date_expired', 'title', 'payment_method', 'vendor', 'tag_value', 'is_paid']


class VendorOrderTable(tables.Table):
    action = tables.TemplateColumn(
        "<a href='{{ record.get_edit_url }}' class='btn btn-primary btn-round'><i class='fa fa-edit'></a>",
        orderable=False,
    )

    class Meta:
        model = Invoice
        template_name = 'django_tables2/bootstrap.html'
        fields = ['date_expired', 'title', 'order_type', 'tag_value', 'tag_final_value']


class VendorProductReportTable(tables.Table):
    action = tables.TemplateColumn(
        "<a href='{{ record.get_edit_url }}' class='btn btn-primary btn-round'><i class='fa fa-edit'></a>",
        orderable=False,
    )

    class Meta:
        model = Product
        template_name = 'django_tables2/bootstrap.html'
        fields = ['title', 'category', 'qty', 'tag_final_price', 'tag_price_buy']


class VendorWarehouseMovementTable(tables.Table):
    action = tables.TemplateColumn(
        "<a href='{{ record.get_edit_url }}' class='btn btn-primary btn-round'><i class='fa fa-edit'></a>",
        orderable=False,
    )
    tag_order_type = tables.Column(verbose_name='Είδος Παραστατικού')
    tag_clean_value = tables.Column(verbose_name='Καθαρή Αξία')
    tag_discount = tables.Column(verbose_name='Έκπτωση')
    tag_total_clean_value = tables.Column(verbose_name='Συνολική Καθαρή Αξία')
    tag_total_taxes = tables.Column(verbose_name='Συνολικοί Φόροι')
    tag_final_value = tables.Column(verbose_name='Αξία Μονάδας')

    class Meta:
        model = InvoiceOrderItem
        template_name = 'django_tables2/bootstrap.html'
        fields = ['sku', 'product', 'order', 'tag_order_type', 'qty',
                  'tag_clean_value', 'tag_discount', 'tag_final_value',
                  'tag_total_clean_value', 'tag_total_taxes'
                  ]
