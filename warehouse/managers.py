from django.db import models
import datetime
from dateutil.relativedelta import relativedelta



class GenericQueryset(models.QuerySet):

    def is_active(self):
        return self.filter(active=True)

    def filter_by_date(self, date_start, date_end):
        return self.filter(date_expired__range=[date_start, date_end])

    def until_today(self):
        return self.filter(date_expired__lte=datetime.datetime.today())

    def not_paid(self):
        return self.filter(is_paid=False)

    def invoices_per_store(self, store):
        return self.filter(category__store=store)

    def until_today_not_paid(self):
        return self.filter(is_paid=False, date_expired__lte=datetime.datetime.today())

    def until_next_ten_days_not_paid(self):
        return self.filter(is_paid=False, date_expired__lte=datetime.datetime.today()+datetime.timedelta(days=10))


class BillingManager(models.Manager):

    def get_queryset(self):
        return GenericQueryset(self.model, using=self._db)


class PayrollManager(models.Manager):

    def get_queryset(self):
        return GenericQueryset(self.model, using=self._db)


class InvoiceManager(models.Manager):

    def only_invoices(self):
        return self.filter(order_type__in=['1', '2',])

    def this_month_invoices(self):
        first_day = datetime.datetime.today().replace(day=1)
        last_day = datetime.datetime.today()
        return self.only_invoices().filter(date_expired__range=[first_day, last_day])

    def last_month_invoices(self):
        first_day = datetime.datetime.today().replace(day=1) - relativedelta(months=1)
        last_day = datetime.datetime.today().replace(day=1) - relativedelta(days=1)
        return self.only_invoices().filter(date_expired__range=[first_day, last_day])

    def not_paid(self):
        return self.only_invoices().filter(is_paid=False)


class ExpenseCategoryManager(models.Manager):

    def get_queryset(self):
        return GenericQueryset(self.model, using=self._db)


class GeneralManager(models.Manager):

    def get_queryset(self):
         return GenericQueryset(self.model, using=self._db,)

    def not_paid(self):
        return self.get_queryset().filter(is_paid=False)