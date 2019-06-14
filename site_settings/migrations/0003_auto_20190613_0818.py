# Generated by Django 2.0.7 on 2019-06-13 05:18

from django.db import migrations, models
import site_settings.models


class Migration(migrations.Migration):

    dependencies = [
        ('site_settings', '0002_auto_20190511_0805'),
    ]

    operations = [
        migrations.AddField(
            model_name='banner',
            name='url',
            field=models.URLField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='shipping',
            name='active',
            field=models.BooleanField(default=True, verbose_name='Κατάσταση'),
        ),
        migrations.AlterField(
            model_name='shipping',
            name='additional_cost',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=6, validators=[site_settings.models.validate_positive_decimal], verbose_name='Επιπλέον κόστος'),
        ),
        migrations.AlterField(
            model_name='shipping',
            name='first_choice',
            field=models.BooleanField(default=False, verbose_name='Πρώτη Επιλογή'),
        ),
        migrations.AlterField(
            model_name='shipping',
            name='limit_value',
            field=models.DecimalField(decimal_places=2, default=40, max_digits=6, validators=[site_settings.models.validate_positive_decimal], verbose_name='Μέγιστη Αξία Κόστους'),
        ),
        migrations.AlterField(
            model_name='shipping',
            name='title',
            field=models.CharField(max_length=100, unique=True, verbose_name='Τίτλος'),
        ),
    ]