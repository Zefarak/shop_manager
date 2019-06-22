from django import forms
from django.conf import settings
from catalogue.forms import BaseForm
from catalogue.models import Product

from dal import autocomplete

WAREHOUSE_ORDERS_TRANSCATIONS = settings.WAREHOUSE_ORDERS_TRANSCATIONS
RETAIL_TRANSCATIONS = settings.RETAIL_TRANSCATIONS


class ProductFormWarehouseTranscations(BaseForm, forms.ModelForm):
    class Meta:
        model = Product
        fields = ['active', 'featured_product',
                  'title', 'sku',
                  'vendor', 'order_code',
                  'price_buy', 'order_discount',
                  'brand', 'category',
                  'price', 'price_discount',
                  'qty_measure',
                  'measure_unit',
                  'site_text', 'slug'

                  ]
        widgets = {
            'vendor': autocomplete.ModelSelect2(url='vendors_auto', attrs={'class': 'form-control'}),
            'category': autocomplete.ModelSelect2(url='warehouse_category_auto',
                                                  attrs={'class': 'form-control', 'data-html': True}),
        }


class ProductFormNoWarehouseNoTranscations(BaseForm, forms.ModelForm):
    class Meta:
        model = Product
        fields = ['active', 'featured_product',
                  'title', 'sku',
                  'vendor', 'price_buy',
                  'brand', 'category',
                  'price', 'price_discount',
                  'measure_unit',
                  'site_text', 'slug',
                  'qty_add'
                ]
        widgets = {
            'vendor': autocomplete.ModelSelect2(url='vendors_auto', attrs={'class': 'form-control'}),
            'category': autocomplete.ModelSelect2(url='warehouse_category_auto',
                                                  attrs={'class': 'form-control', 'data-html': True}),
            }


class ProductNoQty(BaseForm, forms.ModelForm):
    class Meta:
        model = Product
        fields = ['title', 'sku',
                  'vendor', 'order_code',
                  'price_buy', 'order_discount',
                  'brand', 'category',
                  'price', 'price_discount',
                  'qty_measure', 'measure_unit',
                  'site_text', 'slug',
                  'active', 'featured_product'
                ]
        widgets = {
            'vendor': autocomplete.ModelSelect2(url='vendors_auto', attrs={'class': 'form-control'}),
            'category': autocomplete.ModelSelect2(url='warehouse_category_auto', attrs={'class': 'form-control'}),
        }


ProductForm = ProductFormNoWarehouseNoTranscations
if WAREHOUSE_ORDERS_TRANSCATIONS:
    ProductForm = ProductFormWarehouseTranscations