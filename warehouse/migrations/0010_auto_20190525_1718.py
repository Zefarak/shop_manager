# Generated by Django 2.0.7 on 2019-05-25 14:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('warehouse', '0009_auto_20190520_1150'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invoice',
            name='taxes_modifier',
            field=models.CharField(choices=[('1', 13), ('2', 23), ('3', 24), ('4', 0)], default='3', max_length=1, verbose_name='ΦΠΑ'),
        ),
    ]
