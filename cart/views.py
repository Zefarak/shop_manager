from django.shortcuts import HttpResponseRedirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, UpdateView, CreateView
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.urls import reverse
from catalogue.models import Product
from .models import CartItem, Cart
from .forms import CartForm
from .tables import CartTable
from .tools import add_to_cart, add_to_cart_with_attr, remove_from_cart_with_attr

from django_tables2 import RequestConfig


@method_decorator(staff_member_required, name='dispatch')
class CartListView(ListView):
    model = Cart
    template_name = 'dashboard/list_page.html'

    def get_queryset(self):
        queryset = Cart.filter_data(self.request)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        page_title, back_url, create_url = 'Καλάθια', reverse('point_of_sale:home'), reverse('cart:cart_create')
        queryset_table = CartTable(self.object_list)
        RequestConfig(self.request).configure(queryset_table)
        # filters
        search_filter = [True]*1
        context.update(locals())
        return context


@method_decorator(staff_member_required, name='dispatch')
class CreateCartView(CreateView):
    template_name = 'dashboard/form.html'
    model = Cart
    form_class = CartForm
    success_url = reverse_lazy('cart:cart_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form_title, back_url = 'Νέο Καλάθι', self.success_url

        context.update(locals())
        return context

    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'Νέο Καλάθι Προστέθηκε')
        return super().form_valid(form)


@method_decorator(staff_member_required, name='dispatch')
class CartUpdateView(UpdateView):
    model = Cart
    template_name = 'dashboard/form.html'
    form_class = CartForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        back_url = self.request.GET.get('back_url', reverse('cart:cart_list'))
        context.update(locals())
        return context


def check_cart_movement(request, pk, action):
    if action == 'add':
        product = get_object_or_404(Product, id=pk)
        add_to_cart_with_attr(product) if product.have_attr else add_to_cart(request, product)
        messages.success(request, f'{product} added to the cart.')
    if action == 'remove':
        cart_item = get_object_or_404(CartItem, id=pk)
        remove_from_cart_with_attr() if cart_item.have_attributes else cart_item.delete()
        messages.warning(request, f'{cart_item} is deleted.')
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def ajax_cart_change_qty(request, pk):
    instance = get_object_or_404(CartItem, id=pk)
    new_qty = request.GET.get('qty', 1)
    new_qty = int(new_qty)
    instance.qty = new_qty
    instance.save()
    instance.refresh_from_db()
    cart = instance.cart
    cart.refresh_from_db()
    data = dict()
    data['result'] = render_to_string(template_name='cart/ajax_cart_container.html',
                                      request=request,
                                      context={'cart': cart})
    return JsonResponse(data)
