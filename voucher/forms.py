from django import forms
from .models import Voucher


class BaseForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super(BaseForm, self).__init__(*args, **kwargs)
        for field, field_name in self.fields.items():
            field.widget['class'] = 'form-control'


class VoucherForm(BaseForm, forms.ModelForm):

    class Meta:
        model = Voucher
        fields ='__all__'