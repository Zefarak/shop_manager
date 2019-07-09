from django.views.generic import TemplateView, ListView, CreateView, UpdateView
from django.shortcuts import reverse, get_object_or_404, redirect, render, HttpResponseRedirect
from django.db.models import Sum
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from catalogue.models import Product
from catalogue.product_attritubes import Attribute
from .models import Order, OrderItem, OrderItemAttribute, OrderProfile
from .address_models import ShippingAddress
from .forms import OrderCreateForm, OrderCreateCopyForm, OrderUpdateForm, forms, OrderAttributeCreateForm
from site_settings.models import PaymentMethod
from accounts.models import Profile
from accounts.forms import ProfileForm
from cart.models import Cart, CartItem
from .tools import generate_or_remove_queryset
from .tables import ProfileTable, OrderTable, OrderItemListTable
from site_settings.constants import CURRENCY
from django_tables2 import RequestConfig
import datetime


@method_decorator(staff_member_required, name='dispatch')
class DashboardView(TemplateView):
    template_name = 'point_of_sale/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        qs_today = Order.objects.filter(date_expired=datetime.datetime.now())
        today_sells = qs_today.filter(order_type__in=['r', 'e']).aggregate(Sum('final_value'))['final_value__sum'] \
            if qs_today.filter(order_type__in=['r', 'e']).exists() else 0.00
        today_returns = qs_today.filter(order_type__in=['b', 'c', 'wr']).aggregate(Sum('final_value'))['final_value__sum']\
            if qs_today.filter(order_type__in=['b', 'c', 'wr']).exists() else 0.00
        today_sells, today_returns = f'{today_sells} {CURRENCY}', f'{today_returns} {CURRENCY}'
        costumers_dept = f'0.00 {CURRENCY}'
        billings = OrderTable(Order.objects.all())
        context.update(locals())
        return context


@method_decorator(staff_member_required, name='dispatch')
class OrderListView(ListView):
    template_name = 'dashboard/list_page.html'
    model = Order
    paginate_by = 50

    def get_queryset(self):
        qs = Order.objects.all()
        qs = Order.eshop_orders_filtering(self.request, qs)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        queryset_table = OrderTable(self.object_list)
        page_title, create_url, back_url = ['Παταστατικά Πωλήσεων', reverse('point_of_sale:order_create'),
                                            reverse('point_of_sale:home')]

        #  filters
        search_filter, date_filter, paid_filter, costumer_filter = [True]*4

        # print
        print_button, print_url = True, reverse('dashboard:home')

        # report
        reports, report_url = True, reverse('dashboard:home')
        context.update(locals())
        return context


@method_decorator(staff_member_required, name='dispatch')
class SellListView(ListView):
    template_name = 'point_of_sale/order-list.html'
    model = Order
    paginate_by = 30

    def get_queryset(self):
        queryset = Order.my_query.get_queryset().sells()
        queryset = Order.eshop_orders_filtering(self.request, queryset)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        page_title, back_url, create_url = 'Πωλήσεις', reverse('point_of_sale:home'), reverse('point_of_sale:order_create')
        queryset_table = OrderTable(self.object_list)
        RequestConfig(self.request).configure(queryset_table)
        #  filters
        search_filter, date_filter, costumer_filter, paid_filter = [True]*4

        context.update(locals())
        return context


@method_decorator(staff_member_required, name='dispatch')
class CreateOrderView(CreateView):
    model = Order
    form_class = OrderCreateForm
    template_name = 'dashboard/form.html'

    def get_success_url(self):
        self.new_object.refresh_from_db()
        return reverse('point_of_sale:order_detail', kwargs={'pk': self.new_object.id})

    def get_initial(self):
        initial = super().get_initial()
        my_qs = PaymentMethod.objects.filter(title='Cash')
        if my_qs.exists():
            initial['payment_method'] = my_qs.first()
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form_title = 'Δημιουργία Νέου Παραστατικού'
        back_url = self.request.META.get('HTTP_REFERER')
        context.update(locals())
        return context

    def form_valid(self, form):
        object = form.save()
        object.refresh_from_db()
        self.new_object = object
        return super().form_valid(form)


@method_decorator(staff_member_required, name='dispatch')
class OrderUpdateView(UpdateView):
    model = Order
    form_class = OrderUpdateForm
    template_name = 'point_of_sale/order-detail.html'

    def get_initial(self):
        initial = super(OrderUpdateView, self).get_initial()
        initial['date_expired'] = datetime.datetime.strftime(self.object.date_expired, '%Y-%m-%d')
        return initial

    def get_success_url(self):
        return reverse('point_of_sale:order_detail', kwargs={'pk': self.kwargs['pk']})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        homepage_cookie = self.request.COOKIES.get('order_redirect', None)
        products = Product.my_query.active()[:12]
        instance = self.object
        is_return = True if self.object.order_type in ['b', 'wr'] else False
        profile_detail, created = OrderProfile.objects.get_or_create(order_related=instance)
        context.update(locals())
        return context


@staff_member_required
def check_product(request, pk, dk):
    instance = get_object_or_404(Product, id=dk)
    if instance.product_class.have_attribute:
        return redirect(reverse('point_of_sale:add_product_attr', kwargs={'pk': pk, 'dk': dk}))
    else:
        return redirect(reverse('point_of_sale:add_product', kwargs={'pk': pk, 'dk': dk}))


@staff_member_required
def add_to_order_with_attr(request, pk, dk):
    instance = get_object_or_404(Product, id=dk)
    order = get_object_or_404(Order, id=pk)
    form_title, back_url = f'Add {instance.title}', order.get_edit_url()
    order_item_qs = OrderItem.objects.filter(title=instance, order=order)
    order_item = order_item_qs.first() if order_item_qs.exists() else None
    qs = instance.attr_class.all().filter(class_related__have_transcations=True)
    attri_class = qs.first() if qs.exists() else None
    if attri_class is None:
        messages.warning(request, 'Δε έχετε επλέξει μεγεθολόγιο')
        return redirect(order.get_edit_url())
    return render(request, 'point_of_sale/add_to_order_with_attr.html', context=locals())


@staff_member_required
def order_item_edit_with_attr(request, pk):
    instance = get_object_or_404(OrderItem, id=pk)
    product = instance.title
    selected_attr = instance.attributes.all()
    return render(request, 'point_of_sale/order-item-edit.html', context=locals())


@staff_member_required
def delete_order(request, pk):
    instance = get_object_or_404(Order, id=pk)
    for ele in instance.order_items.all():
        ele.delete()
    instance.delete()
    return redirect(reverse('point_of_sale:order_list'))


@method_decorator(staff_member_required, name='dispatch')
class OrderItemListView(ListView):
    model = OrderItem
    template_name = 'dashboard/list_page.html'
    paginate_by = 50

    def get_queryset(self):
        qs = OrderItem.objects.all()
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        back_url = reverse('point_of_sale:home')
        queryset_table = OrderItemListTable(self.object_list)
        RequestConfig(self.request).configure(queryset_table)

        # filters
        date_filter, search_filter = [True]*2
        context.update(locals())
        return context


@method_decorator(staff_member_required, name='dispatch')
class CostumerListView(ListView):
    model = Profile
    template_name = 'dashboard/list_page.html'
    paginate_by = 50

    def get_queryset(self):
        qs = Profile.objects.all()
        qs = Profile.filters_data(self.request, qs)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        page_title, back_url, create_url = 'Πελάτες', reverse('point_of_sale:home'), reverse('point_of_sale:costumer_create_view')
        queryset_table = ProfileTable(self.object_list)
        RequestConfig(self.request).configure(queryset_table)
        search_filter, balance_name = [True] * 2

        # report
        reports, report_url = True, reverse('point_of_sale:ajax_costumer_report')
        ajax_search_url = reverse('point_of_sale:ajax_costumer_search')

        # filters
        search_filter, balance_filter = [True] * 2
        context.update(locals())
        return context


@method_decorator(staff_member_required, name='dispatch')
class CostumerCreateView(CreateView):
    form_class = ProfileForm
    template_name = 'dashboard/form.html'
    model = Profile
    success_url = reverse_lazy('point_of_sale:costumer_list_view')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        back_url, delete_url = self.success_url, None
        form_title = 'Δημιουργία Πελάτη'
        context.update(locals())
        return context

    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'Νέος Πελάτης Προστέθηκε')
        return super().form_valid(form)


@method_decorator(staff_member_required, name='dispatch')
class CostumerUpdateView(UpdateView):
    form_class = ProfileForm
    template_name = 'dashboard/form.html'
    model = Profile
    success_url = reverse_lazy('point_of_sale:costumer_list_view')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        back_url, delete_url = self.success_url, self.object.get_delete_url()
        form_title = f'Επεξεργασία {self.object}'
        context.update(locals())
        return context

    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'Ο Πελάτης Επεξεργάστηκε.')
        return super().form_valid(form)


@staff_member_required
def delete_costumer_view(request, pk):
    instance = get_object_or_404(Profile, id=pk)
    if instance.user:
        return redirect(reverse('point_of_sale:costumer_list_view'))
    instance.delete()
    return redirect(reverse('point_of_sale:costumer_list_view'))


@method_decorator(staff_member_required, name='dispatch')
class CostumerAccountCardView(ListView):
    model = Order
    template_name = 'point_of_sale/costumer-list-view.html'
    paginate_by = 20

    def get_queryset(self):
        self.instance = get_object_or_404(Profile, id=self.kwargs['pk'])
        qs = self.instance.profile_orders.all()
        qs = Order.eshop_orders_filtering(self.request, qs)
        return qs

    def get_context_data(self, **kwargs):
        context = super(CostumerAccountCardView, self).get_context_data(**kwargs)
        page_title = f'{self.instance}'
        total_incomes = self.object_list.aggregate(Sum('final_value'))['final_value__sum']\
            if self.object_list.exists() else 0.00
        not_paid_orders = Order.my_query.get_queryset().not_paid_sells().filter(profile=self.instance)
        queryset_table = OrderTable(self.object_list)
        RequestConfig(self.request).configure(queryset_table)
        # filters
        search_filter, paid_filter, date_filter = [True]*3
        currency, instance, back_url = CURRENCY, self.instance, reverse('point_of_sale:costumer_list_view')  # to this to added to local
        context.update(locals())
        return context

    def render_to_response(self, context, **response_kwargs):
        response = super().render_to_response(context, **response_kwargs)
        response.set_cookie('order_redirect', 'costumers')
        return response