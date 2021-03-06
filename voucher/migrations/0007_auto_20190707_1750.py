# Generated by Django 2.0 on 2019-07-07 14:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('voucher', '0006_remove_voucherrules_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='voucherrules',
            name='benefit_type',
            field=models.CharField(choices=[('Percentage', "Discount is a percentage off of the product's value"), ('Absolute', "Discount is a fixed amount off of the product's value"), ('Multibuy', 'Discount is to give the cheapest product for free'), ('Fixed price', 'Get the products that meet the condition for a fixed price'), ('Shipping absolute', 'Discount is a fixed amount of the shipping cost'), ('Shipping fixed price', 'Get shipping for a fixed price'), ('Shipping percentage', 'Discount is a percentage off of the shipping cost')], default='Percentage', max_length=128, verbose_name='Discount Type'),
        ),
        migrations.AddField(
            model_name='voucherrules',
            name='value',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=12),
        ),
    ]
