from django.contrib import admin

from .models import Voucher, VoucherRules, ProductRange, Benefit


@admin.register(Voucher)
class VoucherAdmin(admin.ModelAdmin):
    pass


@admin.register(VoucherRules)
class VoucherRulesAdmin(admin.ModelAdmin):
    pass


@admin.register(ProductRange)
class ProductRangeAdmin(admin.ModelAdmin):
    pass


@admin.register(Benefit)
class BenefitAdmin(admin.ModelAdmin):
    pass