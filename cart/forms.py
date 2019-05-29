from django import forms
from django.forms import formset_factory
from .models import Attribute, Cart


class BaseForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'


class CartForm(BaseForm, forms.ModelForm):

    class Meta:
        model = Cart
        fields = '__all__'
        read_only = ['cart_id']


class CartAttributeForm(forms.Form):
    attributes = forms.ModelChoiceField(queryset=Attribute.objects.all())


CartAttributeFormset = formset_factory(CartAttributeForm, extra=2)
