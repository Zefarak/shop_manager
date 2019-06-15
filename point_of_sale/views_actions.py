from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import HttpResponseRedirect, get_object_or_404, render
from django.shortcuts import redirect, reverse
from accounts.models import Profile
from .models import Order, OrderItem
from .forms import OrderCreateCopyForm
from site_settings.models import PaymentMethod
import datetime


@staff_member_required
def auto_create_retail_order(request, action):
    # action can be sell, return,
    profile, created = Profile.objects.get_or_create(first_name='Πελατες', last_name='Λιανικής')
    payment_method, created_ = PaymentMethod.objects.get_or_create(title='Μετρητά')
    new_instance = Order.objects.create(
        date_expired=datetime.datetime.now(),
        title='Retail',
        profile=profile,
    )
    if action == 'sell':
        new_instance.title = f'Πώληση... {new_instance.id}'
        new_instance.order_type = 'r'
    if action == 'return':
        new_instance.title = f'Επιστροφή...{new_instance.id}'
        new_instance.order_type = 'b'
        new_instance.status = '5'
    if action == 'ware_income':
        new_instance.title = f'Παραστατικό Εισαγωγής'
        new_instance.order_type = 'wa'
    if action == 'ware_outcome':
        new_instance.title = f'Παραστατικό Εξαγωγής'
        new_instance.order_type = 'wr'
    new_instance.payment_method = payment_method
    new_instance.save()
    new_instance.refresh_from_db()
    if request.session.test_cookie_worked():
        request.session.delete_test_cookie()
    response = redirect(new_instance.get_edit_url())
    response.set_cookie('order_redirect', 'homepage')
    return response


@staff_member_required
def quick_pay_costumer_view(request, pk):
    instance = get_object_or_404(Profile, id=pk)
    instance.value = 0
    instance.save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@staff_member_required
def done_order_view(request, pk, action):
    instance = get_object_or_404(Order, id=pk)
    order_items = instance.order_items.exists()
    if not order_items:
        instance.delete()
        return redirect(reverse('point_of_sale:order_list'))
    if action == 'paid':
        instance.is_paid = True
        instance.status = "8"
    instance.save()
    order_redirect = request.COOKIES.get('order_redirect', None)
    if order_redirect == 'costumers':
        del request.COOKIES['order_redirect']
        return order_redirect(reverse('point_of_sale:costumer_account_card', kwargs={'pk': pk}))
    if order_redirect == 'homepage':
        del request.COOKIES['order_redirect']
        return redirect('point_of_sale:home')
    return redirect(reverse('point_of_sale:order_list'))


@staff_member_required
def create_copy_order(request, pk):
    instance = get_object_or_404(Order, id=pk)
    form_title, back_url = f'Αντιγραφή {instance.title}', reverse('point_of_sale:order_list')
    form = OrderCreateCopyForm(request.POST or None)
    if form.is_valid():
        order_type = form.cleaned_data.get('order_type', instance.order_type)
        new_instance = Order.objects.get(id=pk)
        new_instance.pk = None
        new_instance.date_expired = datetime.datetime.now()
        new_instance.order_type = order_type
        new_instance.save()
        new_instance.refresh_from_db()
        for order_item in instance.order_items.all():
            new_order_item = OrderItem.objects.get(id=order_item.id)
            new_order_item.pk = None
            new_order_item.order = new_instance
            new_order_item.save()
        return redirect(new_instance.get_edit_url())

    context = locals()
    return render(request, 'dashboard/form.html', context)


