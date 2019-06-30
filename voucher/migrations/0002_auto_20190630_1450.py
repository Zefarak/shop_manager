# Generated by Django 2.0 on 2019-06-30 11:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('voucher', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='voucherrules',
            name='date_end',
        ),
        migrations.RemoveField(
            model_name='voucherrules',
            name='start_date',
        ),
        migrations.AlterField(
            model_name='voucher',
            name='end_date',
            field=models.DateField(blank=True, db_index=True, null=True, verbose_name='End Date'),
        ),
        migrations.AlterField(
            model_name='voucher',
            name='start_date',
            field=models.DateField(blank=True, db_index=True, null=True, verbose_name='Start Date'),
        ),
    ]
