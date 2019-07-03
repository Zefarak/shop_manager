# Generated by Django 2.0.7 on 2019-07-02 13:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('site_settings', '0003_auto_20190613_0818'),
    ]

    operations = [
        migrations.AlterField(
            model_name='banner',
            name='active',
            field=models.BooleanField(default=False, verbose_name='Κατάσταση'),
        ),
        migrations.AlterField(
            model_name='banner',
            name='text',
            field=models.CharField(blank=True, max_length=200, null=True, verbose_name='Σχόλεια'),
        ),
        migrations.AlterField(
            model_name='banner',
            name='title',
            field=models.CharField(max_length=100, unique=True, verbose_name='Τίτλος'),
        ),
    ]