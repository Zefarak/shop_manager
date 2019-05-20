import django_tables2 as tables

from .product_attritubes import Attribute


class AttributeTable(tables.Table):
    action = tables.TemplateColumn('')

    class Meta:
        model = Attribute
        template_name = ''
