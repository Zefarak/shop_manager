# Generated by Django 2.0.7 on 2019-06-07 14:50

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('point_of_sale', '0017_auto_20190525_1725'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='date_expired',
            field=models.DateField(default=datetime.date(2019, 6, 7), verbose_name='Ημερομηνία'),
        ),
        migrations.AlterField(
            model_name='order',
            name='profile',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='profile_orders', to='accounts.Profile', verbose_name='Πελάτης'),
        ),
        migrations.AlterField(
            model_name='orderitem',
            name='discount_value',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=20, verbose_name='Έκπτωση %'),
        ),
        migrations.AlterField(
            model_name='orderitem',
            name='final_value',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=20, verbose_name='Αξία'),
        ),
        migrations.AlterField(
            model_name='orderitem',
            name='order',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='order_items', to='point_of_sale.Order', verbose_name='Παραστατικό'),
        ),
        migrations.AlterField(
            model_name='orderitem',
            name='qty',
            field=models.PositiveIntegerField(default=1, verbose_name='Ποσότητα'),
        ),
        migrations.AlterField(
            model_name='orderitem',
            name='title',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='retail_items', to='catalogue.Product', verbose_name='Προϊόν'),
        ),
        migrations.AlterField(
            model_name='orderitem',
            name='value',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=20, verbose_name='Αξία Προϊόντων'),
        ),
    ]
