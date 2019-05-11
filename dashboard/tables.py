from django.utils.html import format_html
import django_tables2 as tables
from catalogue.models import Product, ProductClass
from catalogue.categories import WarehouseCategory, Category
from catalogue.product_details import VendorPaycheck
from catalogue.product_details import Brand


class ImageColumn(tables.Column):

    def render(self, value):
        return format_html('<img class="img img-thumbnail" style="width:50px;height:50px" src="/media/{}" />', value)


class TableProduct(tables.Table):
    action = tables.TemplateColumn("<a href='{{ record.get_edit_url }}' class='btn btn-primary'>Edit</a>", orderable=False)
    tag_final_price = tables.Column(orderable=False, verbose_name='Price')
    tag_price_buy = tables.Column(orderable=False, verbose_name='Price Buy')

    class Meta:
        model = Product
        template_name = 'django_tables2/bootstrap.html'
        fields = ['id', 'title', 'vendor', 'tag_price_buy', 'tag_final_price', 'qty', 'category', 'active', 'action']


class ProductClassTable(tables.Table):
    action = tables.TemplateColumn('<a href="{{ record.get_edit_url }}" class="btn btn-info btn-round">Επεξεργασία</a>')

    class Meta:
        model = ProductClass
        template_name = 'django_tables2/bootstrap.html'
        fields = ['id', 'title', 'have_attribute', 'have_transcations', 'is_service']


class WarehouseCategoryTable(tables.Table):
    action = tables.TemplateColumn("<a href='{{ record.get_edit_url }}' class='btn btn-primary'>Edit</a>",
                                   orderable=False)

    class Meta:
        model = WarehouseCategory
        template_name = 'django_tables2/bootstrap.html'
        fields = ['id', 'title', 'active']


class CategorySiteTable(tables.Table):
    action = tables.TemplateColumn("<a href='{{ record.get_edit_url }}' class='btn btn-primary'>Επεξεργασία</a>",
                                   orderable=False)

    class Meta:
        model = Category
        template_name = 'django_tables2/bootstrap.html'
        fields = ['id', 'title', 'parent', 'active']


class BrandTable(tables.Table):
    action = tables.TemplateColumn("<a href='{{ record.get_edit_url }}' class='btn btn-primary'>Επεξεργασία</a>",
                                   orderable=False)

    class Meta:
        model = Brand
        template_name = 'django_tables2/bootstrap.html'
        fields = ['id', 'title', 'active']


