# Generated by Django 2.0.7 on 2019-07-08 05:42

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('point_of_sale', '0034_auto_20190707_1750'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='date_expired',
            field=models.DateField(default=datetime.date(2019, 7, 8), verbose_name='Ημερομηνία'),
        ),
    ]
