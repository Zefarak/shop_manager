# Generated by Django 2.0.7 on 2019-07-10 11:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0010_delete_vendorpaycheck'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='price',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10, verbose_name='Αρχική Τιμή'),
        ),
        migrations.AlterField(
            model_name='product',
            name='price_buy',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10, verbose_name='Αξία Αγοράς'),
        ),
    ]
