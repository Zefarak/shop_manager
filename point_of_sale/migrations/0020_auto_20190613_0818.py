# Generated by Django 2.0.7 on 2019-06-13 05:18

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('point_of_sale', '0019_auto_20190608_0741'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='date_expired',
            field=models.DateField(default=datetime.date(2019, 6, 13), verbose_name='Ημερομηνία'),
        ),
    ]
