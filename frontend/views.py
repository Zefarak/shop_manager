from django.shortcuts import render, get_object_or_404, reverse, HttpResponseRedirect
from django.views.generic import TemplateView, FormView
from django.forms import formset_factory
from django.contrib import messages
from django.urls import reverse_lazy
from site_settings.models import Banner, PaymentMethod, Shipping
from catalogue.models import Product
from catalogue.product_attritubes import Attribute, AttributeTitle
from .forms import CheckoutForm, VoucherForm
from point_of_sale.models import Order, OrderProfile
from cart.tools import check_or_create_cart
from cart.models import Cart
from .mixins import SearchAndLoginMixin
from point_of_sale.forms import OrderChangeTitle
from voucher.models import Voucher
from cart.forms import CartAttributeForm, CartAttributeFormset


class HomepageView(SearchAndLoginMixin):
    template_name = 'frontend/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        banner = Banner.browser.banner()
        featured_products = Product.my_query.featured_products()
        new_arrivals = Product.my_query.active()[:6]
        context.update(locals())
        return context


class NewProductsView(TemplateView):
    template_name = 'frontend/shop.html'


def product_view(request, slug):
    instance = get_object_or_404(Product, slug=slug)
    count = 0
    attributes = instance.attr_class.all()
    ids = set(ele.id for ele in attributes)
    answers = list(attributes)*2
    extra = attributes.count()
    New_Formset = formset_factory(CartAttributeForm, extra=extra)
    formset = New_Formset(
        initial=[
            {'title': 'Sugar'},
            {'title': 'Milk'}
        ]
    )
    for form in formset:
        print(answers[count])
        form.fields['attributes'].queryset = Attribute.objects.filter(class_related=answers[count])
        count += 1
    context = locals()
    return render(request, 'frontend/product-single.html', context)


class AboutUsView(TemplateView):
    template_name = 'frontend/about.html'


class CartView(TemplateView, FormView):
    template_name = 'frontend/cart.html'
    form_class = VoucherForm
    success_url = reverse_lazy('cart_page')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(locals())
        return context

    def form_valid(self, form):
        title = form.cleaned_data.get('voucher')
        qs = Voucher.objects.filter(code=title.upper())
        voucher = qs.first() if qs.exists() else None
        if not voucher:
            messages.warning(self.request, f'Δεν υπάρχει κουπόνι με κωδικό {title}')
            return super(CartView, self).form_valid(form)

        cart = check_or_create_cart(self.request)
        is_available, message = voucher.check_if_its_available(cart, voucher, self.request.user)
        value = 0
        if is_available:
            cart.vouchers.add(voucher)
            cart.save()
        messages.warning(self.request, f'{message} {value}')
        return super(CartView, self).form_valid(form)


class CheckoutView(FormView):
    template_name = 'frontend/checkout.html'
    form_class = CheckoutForm
    success_url = '/'

    def get_success_url(self):
        self.new_order.refresh_from_db()
        return reverse('order_detail', kwargs={'pk': self.new_order.id})

    def get_initial(self):
        initial = super().get_initial()
        user = self.request.user
        if not user.is_authenticated:
            return initial
        profile = user.profile
        initial['email'] = user.email
        initial['first_name'] = profile.first_name
        initial['last_name'] = profile.last_name
        initial['address'] = profile.shipping_address
        initial['city'] = profile.shipping_city
        initial['postcode'] = profile.shipping_zip_code
        initial['cellphone'] = profile.cellphone
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        payment_methods = PaymentMethod.my_query.active_for_site()
        shipping_methods = Shipping.objects.filter(active=True)
        # del self.request.session['cart_id']
        context.update(locals())
        return context

    def form_valid(self, form):
        cart = check_or_create_cart(self.request)
        if not cart.order_items.exists():
            messages.warning(self.request, 'Δε έχετε προσθέσει Προϊόντα')
            return super().form_valid(form)
        self.new_order = new_order = Order.create_eshop_order(self.request, form, cart)
        cart.status = 'Submitted'
        cart.save()
        new_profile = OrderProfile.create_profile_from_cart(form, new_order)
        del self.request.session['cart_id']
        OrderProfile.create_profile_from_cart(form, new_order)
        return super().form_valid(form)


def order_detail(request, pk):
    order = get_object_or_404(Order, id=pk)
    profile = order.order_profiles.first()
    form = OrderChangeTitle(request.POST or None, instance=order)
    if form.is_valid():
        form.save()
        return HttpResponseRedirect(reverse('order_detail', kwargs={'pk': pk}))
    return render(request, 'frontend/order_detail.html', locals())


def delete_session_view(request):
    del request.session['cart_id']
    return HttpResponseRedirect('/')