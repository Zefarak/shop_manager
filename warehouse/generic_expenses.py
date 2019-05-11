from django.db import models
from django.shortcuts import reverse
from django.db.models.signals import pre_delete, post_delete
from django.db.models import Sum
from django.dispatch import receiver
from .abstract_models import DefaultOrderItemModel,DefaultOrderModel
from .managers import ExpenseCategoryManager


class GenericExpenseCategory(models.Model):
    active = models.BooleanField(default=True)
    title = models.CharField(unique=True, max_length=150)
    balance = models.DecimalField(default=0, decimal_places=2, max_digits=20)
    objects = models.Manager()
    my_query = ExpenseCategoryManager()

    class Meta:
        verbose_name_plural = '7. Γενικά Έξοδα'
        verbose_name = 'Έξοδο'

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        orders = self.expenses.all()
        self.balance = orders.aggregate(Sum('final_value'))['final_value__sum'] if orders else 0
        self.balance -= orders.aggregate(Sum('paid_value'))['paid_value__sum'] if orders else 0
        super(GenericExpenseCategory, self).save(*args, *kwargs)

    def tag_balance(self):
        return f'{self.balance} {CURRENCY}'

    def get_dashboard_url(self):
        return reverse('billings:expense_cate_detail', kwargs={'pk': self.id})

    @staticmethod
    def filters_data(request, queryset):
        search_name = request.GET.get('search_name', None)

        queryset = queryset.filter(title__icontains=search_name) if search_name else queryset
        return queryset


class GenericExpense(DefaultOrderModel):
    category = models.ForeignKey(GenericExpenseCategory,
                                 null=True,
                                 on_delete=models.PROTECT,
                                 related_name='expenses'
                                 )
    objects = models.Manager()


    def tag_model(self):
        return f'Expenses- {self.category}'

    class Meta:
        verbose_name_plural = '3. Εντολή Πληρωμής Γενικών Εξόδων'
        verbose_name = 'Εντολή Πληρωμής'
        ordering = ['is_paid', '-date_expired']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.final_value = self.value
        self.paid_value = self.final_value if self.is_paid else 0
        super().save(*args, **kwargs)
        self.category.save()

    def get_dashboard_url(self):
        return reverse('billings:edit_page', kwargs={'pk': self.id, 'slug': 'edit', 'mymodel': 'expense'})

    def get_paid_url(self):
        return reverse('billings:edit_page', kwargs={'pk': self.id, 'slug': 'paid', 'mymodel': 'expense'})

    def get_delete_url(self):
        return reverse('billings:edit_page', kwargs={'pk': self.id, 'slug': 'delete', 'mymodel': 'expense'})

    def get_dashboard_save_as_url(self):
        return reverse('billings:save_as_view', kwargs={'pk': self.id, 'slug': 'expense'})

    def get_dashboard_list_url(self):
        return reverse('billings:expenses_list')

    def update_category(self):
        self.category.update_balance()

    def destroy_payments(self):
        queryset = self.payment_orders.all()
        for payment in queryset:
            payment.delete()

    @staticmethod
    def filters_data(request, queryset):
        search_name = request.GET.get('search_name', None)
        cate_name = request.GET.getlist('cate_name', None)
        paid_name = request.GET.getlist('paid_name', None)
        date_start, date_end = request.GET.get('date_start', None), request.GET.get('date_end', None)

        if date_start and date_end and date_end > date_start:
            queryset = queryset.filter(date_expired__range=[date_start, date_end])
        queryset = queryset.filter(is_paid=True) if 'paid' in paid_name else queryset.filter(is_paid=False) \
            if 'not_paid' in paid_name else queryset
        queryset = queryset.filter(category__id__in=cate_name) if cate_name else queryset
        queryset = queryset.filter(Q(title__icontains=search_name )|
                                   Q(category__title__icontains=search_name)
                                   ).distinct() if search_name else queryset
        return queryset


@receiver(post_delete, sender=GenericExpense)
def update_expense_category(sender, instance, **kwargs):
    instance.category.update_balance()


@receiver(pre_delete, sender=GenericExpense)
def delete_generic_order_items(sender, instance, **kwargs):
    for order in instance.payment_orders.all(): order.delete()