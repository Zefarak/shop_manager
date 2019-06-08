from django.db import models
from django.shortcuts import reverse
from catalogue.models import Product

CHOICES = (
    ('a', 'Ποσοστό'),
    ('b', 'Ποσό'),
    ('c', 'Ακριβές Ποσό')
)

TYPE = (
    ('a', 'Έκπτωση Brand'),
    ('b', 'Έκπτωση Κατηγοριών'),
    ('c', 'Έκπτωση Προϊόντων')
 )


class ProductDiscount(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True, verbose_name='Κατάσταση')
    date_start = models.DateField(verbose_name='Ημερομηνία Από..',
                                  blank=True,
                                  null=True)
    date_end = models.DateField(verbose_name='Ημερομηνία Μέχρι..',
                                help_text='Αν μείνει κενό διαρκεί για πάντα',
                                blank=True,
                                null=True
                                )
    title = models.CharField(unique=True, max_length=200, verbose_name='Τίτλος')
    my_choices = models.CharField(max_length=1, choices=CHOICES,verbose_name='Τρόπος Έκπτωσεις')
    discount_type = models.CharField(max_length=1, choices=TYPE, verbose_name='Έιδος Έκπτωσης')
    value = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Αξία')
    products_related = models.ManyToManyField(Product)

    def __str__(self):
        return self.title

    def tag_range(self):
        return f'{self.date_start} - {self.date_end}'

    def get_edit_url(self):
        return reverse('dashboard:discount_manager_update', kwargs={'pk': self.id})

    def get_delete_url(self):
        return ''
