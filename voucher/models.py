from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.shortcuts import reverse

from catalogue.models import Product, ProductClass, Category, Brand


class Voucher(models.Model):
    SINGLE_USE, MULTI_USE, ONCE_PER_CUSTOMER = (
        'Single use', 'Multi-use', 'Once per customer')
    USAGE_CHOICES = (
        (SINGLE_USE, _("Can be used once by one customer")),
        (MULTI_USE, _("Can be used multiple times by multiple customers")),
        (ONCE_PER_CUSTOMER, _("Can only be used once per customer")),
    )
    active = models.BooleanField(default=False)
    name = models.CharField(_("Name"), max_length=128, help_text="This will be shown in the checkout"
                                        " and basket once the voucher is"
                                        " entered")
    code = models.CharField(_('Code'), max_length=128, db_index=True, unique=True)
    usage = models.CharField(max_length=128, choices=USAGE_CHOICES, default=MULTI_USE)
    start_date = models.DateField(_('Start Date'), db_index=True, blank=True, null=True)
    end_date = models.DateField(_('End Date'), db_index=True, blank=True, null=True)
    num_basket_additons = models.PositiveIntegerField(default=0)
    num_orders = models.PositiveIntegerField(default=0)
    total_discount = models.DecimalField(decimal_places=2, max_digits=12, default=0.00)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.code = self.code.upper()
        super().save(*args, **kwargs)

    def get_edit_url(self):
        return reverse('vouchers:voucher_detail', kwargs={'pk': self.id})

    def is_expired(self):
        now = timezone.now()
        return self.end_date < now

    def is_available_to_user(self, user=None):
        is_available, message = False, ''
        if self.usage == self.SINGLE_USE:
            is_available = 'Check if used!'
            if not is_available:
                message = _("This voucher has already been used")
        elif self.MULTI_USE:
            is_available = True
        elif self.usage == self.ONCE_PER_CUSTOMER:
            if not user.is_authenticated:
                is_available = False
                message = _('You need to log in to use this voucher')
            else:
                is_available = not False
                if not is_available:
                    message = _('You have laready used this voucher')
            return is_available, message

    def is_available_for_basket(self, basket):
        is_available, message = self.is_available_to_user(user=basket.owner)
        if not is_available:
            return is_available, message

        is_available, message = False, _('This voucher cant be used for this cart')
        #  CHECK ID IS THE BASKET
        return is_available, message

    def record_usage(self, order, user):
        pass


class Benefit(models.Model):
    voucher = models.OneToOneField(Voucher, on_delete=models.CASCADE, related_name='voucher_benefit')
    PERCENTAGE, FIXED, MULTIBUY, FIXED_PRICE = (
        "Percentage", "Absolute", "Multibuy", "Fixed price")
    SHIPPING_PERCENTAGE, SHIPPING_ABSOLUTE, SHIPPING_FIXED_PRICE = (
        'Shipping percentage', 'Shipping absolute', 'Shipping fixed price')
    TYPE_CHOICES = (
        (PERCENTAGE, _("Discount is a percentage off of the product's value")),
        (FIXED, _("Discount is a fixed amount off of the product's value")),
        (MULTIBUY, _("Discount is to give the cheapest product for free")),
        (FIXED_PRICE,
         _("Get the products that meet the condition for a fixed price")),
        (SHIPPING_ABSOLUTE,
         _("Discount is a fixed amount of the shipping cost")),
        (SHIPPING_FIXED_PRICE, _("Get shipping for a fixed price")),
        (SHIPPING_PERCENTAGE, _("Discount is a percentage off of the shipping"
                                " cost")),
    )
    benefit_type = models.CharField(choices=TYPE_CHOICES, default=PERCENTAGE, max_length=128)
    value = models.DecimalField(default=0.00, max_digits=12, decimal_places=2)
    max_affected_items = models.PositiveIntegerField(blank=True, null=True)


class ProductRange(models.Model):
    voucher = models.OneToOneField(Voucher, on_delete=models.CASCADE, related_name='voucher_range')
    include_all_products = models.BooleanField(default=True)
    included_products = models.ManyToManyField(Product, related_name='included_products')
    excluded_products = models.ManyToManyField(Product, related_name='excluded_products')
    classes = models.ManyToManyField(ProductClass)
    included_categories = models.ManyToManyField(Category)
    included_brands = models.ManyToManyField(Brand)


class VoucherRules(models.Model):
    voucher = models.OneToOneField(Voucher, on_delete=models.CASCADE, related_name='voucher_rule')
    SITE, CATEGORY, BRAND, PRODUCTS, SHIPPING_DISCOOUNT = ("Site", "Category", "Brand", "Products", "Shipping Discount")
    TYPE_CHOICES = (
        (SITE, _("Site offer - available to all users and products")),
        (CATEGORY, _("Category offer - only available for certain categories ")),
        (BRAND, _("Brand offer - available to certain brands")),
        (PRODUCTS, _("Products offer - Manual add Products")),
    )
    OPEN, SUSPENDED, CONSUMED = "Open", "Suspended", "Consumed"
    description = models.TextField(blank=True, help_text='Description for the costumers')
    offer_type = models.CharField(choices=TYPE_CHOICES, default=SITE, max_length=128)
    exclusive = models.BooleanField(default=True)
    status = models.CharField(_("Status"), max_length=64, default=OPEN)
    priority = models.IntegerField(default=0, db_index=True)

    max_global_applications = models.PositiveIntegerField(blank=True, null=True)
    max_user_applications = models.PositiveIntegerField(blank=True, null=True)
    max_basket_applications = models.PositiveIntegerField(blank=True, null=True)
    total_discount = models.DecimalField(default=0.00, decimal_places=2, max_digits=12)
    num_applications = models.PositiveIntegerField(default=0)
    num_orders = models.PositiveIntegerField(default=0)






