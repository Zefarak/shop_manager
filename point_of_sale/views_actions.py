from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import redirect, reverse
from accounts.models import Profile
from .models import Order
from site_settings.models import PaymentMethod
import datetime


@staff_member_required
def auto_create_retail_order(request, action):
    # action can be sell, return,
    profile, created = Profile.objects.get_or_create(first_name='Πελατες', last_name='Λιανικής')
    new_instance = Order.objects.create(
        date_expired=datetime.datetime.now(),
        title='Retail',
        profile=profile,
    )
    if action == 'sell':
        new_instance.title = f'Πώληση... {new_instance.id}'
        new_instance.order_type = 'r'
    if action == 'return':
        new_instance.title = f'Επιστροφή...{new_instance.ιd}'
        new_instance.order_type = 'b'
    if action == 'ware_income':
        new_instance.title = f'Παραστατικό Εισαγωγής'
        new_instance.order_type = 'wa'
    if action == 'ware_outcome':
        new_instance.title = f'Παραστατικό Εξαγωγής'
        new_instance.order_type = 'wr'
    new_instance.save()
    return redirect(new_instance.get_edit_url())