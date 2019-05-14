from django.db import models
from django.shortcuts import reverse
from django.db.models.signals import pre_delete, post_delete
from django.db.models import Sum
from django.dispatch import receiver
from .abstract_models import DefaultOrderItemModel,DefaultOrderModel
from .managers import ExpenseCategoryManager
from site_settings.constants import CURRENCY


class GenericPerson(models.Model):
    title = models.CharField(max_length=200)
    notes = models.TextField(blank=True)
    balance = models.DecimalField(default=0.00, decimal_places=2, max_digits=20)
    active = models.BooleanField(default=True)
    phone = models.CharField(max_length=15, blank=True)

    def save(self, **kwargs):
        invoices = self.person_invoices.all().filter(is_paid=False)
        self.balance = invoices.aggregate(Sum('final_value'))['final_value__sum'] if invoices else 0.00
        super().save()

    def __str__(self):
        return self.title

    def get_edit_url(self):
        return reverse('warehouse:generic-expense-person-edit', kwargs={'pk': self.id})

    def get_delete_url(self):
        return reverse('warehouse:generic-expense-person-delete', kwargs={'pk': self.id})

    def tag_balance(self):
        return f'{self.balance} {CURRENCY}'

    @staticmethod
    def filters_data(request, queryset):
        is_active = request.GET.get('active_name', None)
        search_name = request.GET.get('search_name', None)

        queryset = queryset.filter(active=True) if is_active == '1' else queryset.filter(active=False) if is_active == '2'\
            else queryset
        queryset = queryset.filter(title__contains=search_name) if search_name else queryset
        return queryset


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
        orders = self.expenses.all().filter(is_paid=False)
        self.balance = orders.aggregate(Sum('final_value'))['final_value__sum'] if orders else 0.00
        super(GenericExpenseCategory, self).save(*args, *kwargs)

    def tag_balance(self):
        return f'{self.balance} {CURRENCY}'

    def get_edit_url(self):
        return reverse('warehouse:generic-expense-cate-edit', kwargs={'pk': self.id})

    def get_delete_url(self):
        return reverse('warehouse:generic-expense-cate-delete', kwargs={'pk': self.id})

    @staticmethod
    def filters_data(request, queryset):
        search_name = request.GET.get('search_name', None)
        active_name = request.GET.get('active_name', None)
        queryset = queryset.filter(active=True) if active_name == '1' else queryset.filter(active_name=False) \
            if queryset == '2' else queryset
        queryset = queryset.filter(title__contains=search_name) if search_name else queryset
        return queryset


class GenericExpense(DefaultOrderModel):
    category = models.ForeignKey(GenericExpenseCategory,
                                 null=True,
                                 on_delete=models.PROTECT,
                                 verbose_name='Κατηγορία Εξόδων',
                                 related_name='expenses'
                                 )
    person = models.ForeignKey(GenericPerson, blank=True, null=True, on_delete=models.SET_NULL,
                               verbose_name="Εταιρία/'Ατομο", related_name='person_invoices')
    objects = models.Manager()

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
        self.person.save()

    def get_edit_url(self):
        return reverse('warehouse:generic-expense-edit', kwargs={'pk': self.id})

    def get_delete_url(self):
        return reverse('warehouse:generic-expense-delete', kwargs={'pk': self.id})

    def tag_final_value(self):
        return f'{self.final_value} {CURRENCY}'

    @staticmethod
    def filters_data(request, queryset):
        search_name = request.GET.get('search_name', None)
        cate_name = request.GET.getlist('cate_name', None)
        paid_name = request.GET.getlist('paid_name', None)
        employee_name = request.GET.getlist('employee_name', None)
        date_start, date_end = request.GET.get('date_start', None), request.GET.get('date_end', None)
        queryset = queryset.filter(person__id__in=employee_name) if employee_name else queryset
        if date_start and date_end and date_end > date_start:
            queryset = queryset.filter(date_expired__range=[date_start, date_end])
        queryset = queryset.filter(is_paid=True) if 'paid' in paid_name else queryset.filter(is_paid=False) \
            if 'not_paid' in paid_name else queryset
        queryset = queryset.filter(category__id__in=cate_name) if cate_name else queryset
        queryset = queryset.filter(Q(title__icontains=search_name)|
                                   Q(category__title__icontains=search_name)
                                   ).distinct() if search_name else queryset
        return queryset


@receiver(post_delete, sender=GenericExpense)
def update_expense_category(sender, instance, **kwargs):
    instance.person.save()
    instance.category.save()


