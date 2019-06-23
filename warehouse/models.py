from django.db import models
from django.core.exceptions import ValidationError
from django.contrib import messages
from catalogue.product_details import Vendor
from .payroll import *
from .billing import *
from .generic_expenses import *
from .managers import InvoiceManager
from .abstract_models import DefaultOrderModel, DefaultOrderItemModel
from catalogue.models import Product
from catalogue.product_attritubes import Attribute
from site_settings.tools import estimate_date_start_end_and_months
from decimal import Decimal


def upload_image(instance, filename):
    return f'warehouse_images/{instance.order_related.vendor.title}/{instance.order_related.title}/{filename}'


def validate_file(value):
    if value.file.size > 1024*1024*5:
        return ValidationError('This file is biger than 5 mb')


class Invoice(DefaultOrderModel):
    vendor = models.ForeignKey(Vendor, on_delete=models.SET_NULL, null=True, related_name='vendor_orders', verbose_name='Προμηθευτής')
    additional_value = models.DecimalField(default=0.00, max_digits=15, decimal_places=2, verbose_name='Επιπλέον Κόστος')
    clean_value = models.DecimalField(default=0.00, max_digits=15, decimal_places=2, verbose_name='Καθαρή Αξία')
    taxes_modifier = models.CharField(max_length=1, choices=TAXES_CHOICES, default='3', verbose_name='ΦΠΑ')
    taxes = models.DecimalField(default=0.00, max_digits=15, decimal_places=2, verbose_name='Φόρος')
    order_type = models.CharField(default=1, max_length=1, choices=WAREHOUSE_ORDER_TYPE, verbose_name='Είδος')

    objects = models.Manager()
    broswer = InvoiceManager()

    class Meta:
        verbose_name_plural = "1. Warehouse Invoice"
        ordering = ['-date_expired']

    def save(self, *args, **kwargs):
        order_items = self.order_items.all()
        if order_items.exists():
            self.clean_value = order_items.aggregate(Sum('total_clean_value'))['total_clean_value__sum']
            self.taxes = Decimal(self.clean_value) * Decimal((self.get_taxes_modifier_display())/100)
        else:
            self.clean_value, self.taxes, self.final_value = 0, 0, 0

        self.final_value = self.clean_value + self.taxes + self.additional_value
        self.paid_value = self.update_paid_value()

        super().save(*args, **kwargs)
        self.vendor.update_output_value()

    def __str__(self):
        return self.title

    def update_paid_value(self):
        qs = self.payments.filter(is_paid=True)
        paid_value = qs.aggregate(Sum('value'))['value__sum'] if qs.exists() else 0.00
        return paid_value


    def tag_discount(self):
        return f'{self.discount} %'

    def tag_not_paid_value(self):
        value = self.final_value - self.paid_value
        return f'{value} {CURRENCY}'

    def tag_clean_value(self):
        return f'{self.clean_value} {CURRENCY}'

    def tag_taxes(self):
        return f'{self.taxes} {CURRENCY}'

    def tag_additional_value(self):
        if self.additional_value >= 0:
            return f'Added {self.additional_value}'
        return f'Removed {self.additional_value}'

    def get_edit_url(self):
        return reverse('warehouse:update_order', kwargs={'pk': self.id})

    def get_payment_url(self):
        return reverse('warehouse:invoice_paycheck_list', kwargs={'pk': self.id})

    def get_delete_url(self):
        return reverse('warehouse:invoice_delete', kwargs={'pk': self.id})

    def image(self):
        qs = self.images.all().filter(is_first=True)
        return qs.first() if qs.exists() else None

    @staticmethod
    def filter_data(request, queryset):
        search_name = request.GET.get('search_name', None)
        vendor_name = request.GET.getlist('vendor_name', None)
        paid_name = request.GET.get('paid_name', None)
        date_start, date_end, date_range, months_list = estimate_date_start_end_and_months(request)
        payment_name = request.GET.getlist('payment_name', None)
        order_type_name = request.GET.getlist('order_type_name', None)
        try:
            queryset = queryset.filter(order_type__in=order_type_name) if order_type_name else queryset
            queryset = queryset.filter(vendor__id__in=vendor_name) if vendor_name else queryset
            queryset = queryset.filter(Q(title__contains=search_name) |
                                       Q(vendor__title__contains=search_name)
                                       ).dinstict() if search_name else queryset
            queryset = queryset.filter(date_expired__range=[date_start, date_end]) if date_start else queryset
            queryset = queryset.filter(is_paid=True) if paid_name == '1' else queryset.filter(is_paid=False) \
                if paid_name == '2' else queryset
            queryset = queryset.filter(payment_name__id__in=payment_name) if payment_name else queryset
        except:
            queryset = queryset
        return queryset


class InvoiceImage(models.Model):
    order_related = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='images')
    file = models.FileField(upload_to=upload_image, null=True, validators=[validate_file, ])
    is_first = models.BooleanField(default=True)

    def __str__(self):
        return '%s-%s' % (self.order_related.title, self.id)

    def get_edit_url(self):
        return reverse('warehouse:update-order-image', kwargs={'pk': self.id})

    def get_delete_url(self):
        return reverse('warehouse:delete-order-image', kwargs={'pk': self.id})


class InvoiceOrderItem(DefaultOrderItemModel):
    sku = models.CharField(max_length=150, null=True)
    order = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='order_items')
    product = models.ForeignKey(Product,
                                on_delete=models.CASCADE,
                                null=True,
                                related_name='invoice_products'
                                )
    attribute = models.BooleanField(default=False)
    unit = models.CharField(max_length=1, choices=UNIT, default='1', verbose_name='Μονάδα Μέτρησης')
    total_clean_value = models.DecimalField(default=0, max_digits=15, decimal_places=2, verbose_name='Συνολική Καθαρή Αξία')
    total_final_value = models.DecimalField(default=0, max_digits=14, decimal_places=2, verbose_name='Συνολίκή Αξία')

    def __str__(self):
        return f'{self.product}'

    def save(self, *args, **kwargs):
        if self.product.have_attr:
            self.attribute = True
            self.qty = self.my_attributes.all().aggregate(Sum('qty'))['qty__sum'] if self.my_attributes.all().exists() else 0
        self.final_value = Decimal(self.value) * (100 - self.discount_value) / 100
        self.total_clean_value = Decimal(self.final_value) * Decimal(self.qty)
        self.total_final_value = Decimal(self.total_clean_value) * Decimal((100 + self.order.get_taxes_modifier_display()) / 100)
        super().save(*args, **kwargs)
        self.product.price_buy = self.value
        self.product.order_discount = self.discount_value
        self.product.order_code = self.sku

        self.order.save()

        if WAREHOUSE_ORDERS_TRANSCATIONS:
            self.product.warehouse_calculations()

    def get_edit_url(self):
        return reverse('warehouse:order-item-update', kwargs={'pk': self.id})

    def get_delete_url(self):
        return reverse('warehouse:order-item-delete', kwargs={'pk': self.id})

    def get_copy_url(self):
        return reverse('warehouse:invoice_create_copy', kwargs={'pk': self.id})

    def remove_from_order(self, qty):
        if WAREHOUSE_ORDERS_TRANSCATIONS:
            product = self.product
            product.qty -= qty
            product.save()
        self.order.save()

    def quick_add_to_order(self, qty):
        qty = Decimal(qty) if qty else 0
        if WAREHOUSE_ORDERS_TRANSCATIONS:
            product = self.product
            product.qty += qty
            product.save()

    def tag_discount(self):
        return f'{self.discount_value} %'

    def tag_total_clean_value(self):
        return f'{self.total_clean_value} {CURRENCY}'

    def tag_final_value(self):
        return f'{self.final_value} {CURRENCY}'

    def tag_total_final_value(self):
        return '%s %s' % (round(self.total_value_with_taxes), CURRENCY)

    def tag_total_taxes(self):
        taxes = self.total_value_with_taxes - self.total_clean_value
        return f'{taxes} {CURRENCY}'

    def tag_order(self):
        return f"{self.order.title} - {self.order.vendor.title}"
    tag_order.short_description = 'Παραστατικό'

    def tag_product(self):
        return f'{self.product.title}'
    tag_product.short_description = 'Προϊόν'

    @staticmethod
    def filters_data(request, queryset):
        category_name = request.GET.getlist('category_name', None)
        brand_name = request.GET.getlist('brand_name', None)
        vendor_name = request.GET.getlist('vendor_name', None)
        queryset = queryset.filter(product__category__id__in=category_name) if category_name else queryset
        queryset = queryset.filter(product__brand__id__in=brand_name) if brand_name else queryset
        queryset = queryset.filter(product__vendor__id__in=vendor_name) if vendor_name else queryset
        return queryset


@receiver(post_delete, sender=InvoiceOrderItem)
def update_qty_on_delete(sender, instance, *args, **kwargs):
    product, order, self = instance.product, instance.order, instance
    product.save() if WAREHOUSE_ORDERS_TRANSCATIONS else ''
    self.order.save()


class InvoiceAttributeItem(models.Model):
    order_item = models.ForeignKey(InvoiceOrderItem, on_delete=models.CASCADE, related_name='my_attributes')
    attribute_related = models.ForeignKey(Attribute, on_delete=models.PROTECT, related_name='invoice_attributes')
    qty = models.IntegerField(default=1)

    def __str__(self):
        return f'{self.order_item} - {self.attribute_related}'


class VendorPaycheck(models.Model):
    timestamp = models.DateField(auto_now_add=True)
    title = models.CharField(max_length=150, verbose_name='Τίτλος')
    date_expired = models.DateField(verbose_name='Ημερμηνία λήξης')
    payment_method = models.ForeignKey(PaymentMethod, null=True, on_delete=models.SET_NULL, verbose_name='Τρόπος Πληρωμής')
    value = models.DecimalField(default=0.00, decimal_places=2, max_digits=20, verbose_name='Αξία')
    paid_value = models.DecimalField(default=0.00, decimal_places=2, max_digits=20, verbose_name='Πληρωμένη Αξία')
    order_related = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='payments', verbose_name='Τιμολόγιο')
    is_paid = models.BooleanField(default=False, verbose_name='Πληρωμένο')
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='vendor_paychecks', verbose_name='Προμηθευτής')

    def __str__(self):
        return f'{self.title} - {self.vendor}'

    def save(self, *args, **kwargs):
        if self.is_paid:
            self.paid_value = self.value
        super().save(*args, **kwargs)
        self.order_related.save() if self.order_related else self.vendor.update_input_value()

    def get_edit_url(self):
        return reverse('warehouse:paycheck_detail', kwargs={'pk': self.id})

    def get_invoice_edit_url(self):
        return reverse('warehouse:invoice_paycheck_update', kwargs={'pk': self.id})

    def get_delete_url(self):
        return reverse('warehouse:paycheck_delete', kwargs={'pk': self.id})

    def tag_value(self):
        return f'{self.value} {CURRENCY}'

    @staticmethod
    def filters_data(request, queryset):
        sorted_name = request.GET.get('sort', None)
        date_start, date_end, date_range, months_list = estimate_date_start_end_and_months(request)
        paid_name = request.GET.get('paid_name', None)
        search_name = request.GET.get('search_name', None)
        vendor_name = request.GET.get('vendor_name')
        try:
            queryset = queryset.order_by(sorted_name)
        except:
            queryset = queryset
        queryset = queryset.filter(is_paid=True) if paid_name == '1' else \
            queryset.filter(is_paid=False) if queryset == '2' else queryset
        queryset = queryset.filter(date_expired__range=[date_start, date_end])
        queryset = queryset.filter(Q(title__contains=search_name) |
                                   Q(vendor__title__contains=search_name)
                                   ).distinct() if search_name else queryset
        queryset = queryset.filter(vendor__id__in=vendor_name) if vendor_name else queryset
        return queryset


@receiver(post_delete, sender=Invoice)
def update_warehouse_on_invoice_delete(sender, instance, **kwargs):
    if WAREHOUSE_ORDERS_TRANSCATIONS:
        instance.vendor.update_balance() if instance.vendor else ''


@receiver(post_delete, sender=InvoiceOrderItem)
def update_warehouse_on_invoice_item_delete(sender, instance, **kwargs):
    if WAREHOUSE_ORDERS_TRANSCATIONS:
        instance.product.warehouse_calculations() if not instance.product.have_attr else ''
    instance.order.save()


@receiver(post_save, sender=InvoiceAttributeItem)
def update_warehouse(sender, instance, **kwargs):
    if WAREHOUSE_ORDERS_TRANSCATIONS:
        instance.attribute_related.save()
