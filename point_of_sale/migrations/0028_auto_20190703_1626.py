# Generated by Django 2.0.7 on 2019-07-03 13:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('point_of_sale', '0027_auto_20190703_1451'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='billing_address',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='point_of_sale.BillingAddress'),
        ),
        migrations.AlterField(
            model_name='order',
            name='shipping_address',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='point_of_sale.ShippingAddress'),
        ),
    ]