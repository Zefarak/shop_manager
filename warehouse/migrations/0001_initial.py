# Generated by Django 2.0 on 2019-04-17 15:20

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import uuid
import warehouse.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('site_settings', '0001_initial'),
        ('catalogue', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='BillCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('active', models.BooleanField(default=True)),
                ('title', models.CharField(max_length=150)),
                ('balance', models.DecimalField(decimal_places=2, default=0, max_digits=50)),
                ('store', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='site_settings.Store')),
            ],
            options={
                'verbose_name_plural': '1. Manage Bill Category',
            },
        ),
        migrations.CreateModel(
            name='BillInvoice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uid', models.UUIDField(default=uuid.uuid4, editable=False, verbose_name='Friendly ID')),
                ('title', models.CharField(max_length=150, verbose_name='Title')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('edited', models.DateTimeField(auto_now=True)),
                ('notes', models.TextField(blank=True, null=True, verbose_name='Notes')),
                ('date_expired', models.DateField(default=django.utils.timezone.now, verbose_name='Date expired')),
                ('value', models.DecimalField(decimal_places=2, default=0, max_digits=20, verbose_name='Value')),
                ('taxes', models.DecimalField(decimal_places=2, default=0, max_digits=20, verbose_name='Taxes')),
                ('paid_value', models.DecimalField(decimal_places=2, default=0, max_digits=20, verbose_name='Paid Value')),
                ('final_value', models.DecimalField(decimal_places=2, default=0, max_digits=20, verbose_name='Final Value')),
                ('discount', models.DecimalField(decimal_places=2, default=0, max_digits=20, verbose_name='Discount')),
                ('is_paid', models.BooleanField(default=False, verbose_name='Is Paid')),
                ('printed', models.BooleanField(default=False, verbose_name='Printed')),
                ('category', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='bills', to='warehouse.BillCategory', verbose_name='Bill')),
                ('payment_method', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='site_settings.PaymentMethod', verbose_name='PaymentMethod')),
                ('user_account', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Bill Invoice',
                'verbose_name_plural': '2. Bill Invoice',
                'ordering': ['-date_expired'],
            },
        ),
        migrations.CreateModel(
            name='Employee',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('active', models.BooleanField(default=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('edited', models.DateTimeField(auto_now=True)),
                ('title', models.CharField(max_length=64, unique=True, verbose_name='Name')),
                ('phone', models.CharField(blank=True, max_length=10, verbose_name='Phone')),
                ('phone1', models.CharField(blank=True, max_length=10, verbose_name='Cell Phone')),
                ('date_started', models.DateField(default=django.utils.timezone.now, verbose_name='Date started')),
                ('balance', models.DecimalField(decimal_places=2, default=0, max_digits=50, verbose_name='Balance')),
                ('vacation_days', models.IntegerField(default=0, verbose_name='Remaining Vacation Days')),
            ],
            options={
                'verbose_name': 'Υπάλληλος',
                'verbose_name_plural': '4. Employee',
            },
        ),
        migrations.CreateModel(
            name='Invoice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uid', models.UUIDField(default=uuid.uuid4, editable=False, verbose_name='Friendly ID')),
                ('title', models.CharField(max_length=150, verbose_name='Title')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('edited', models.DateTimeField(auto_now=True)),
                ('notes', models.TextField(blank=True, null=True, verbose_name='Notes')),
                ('date_expired', models.DateField(default=django.utils.timezone.now, verbose_name='Date expired')),
                ('value', models.DecimalField(decimal_places=2, default=0, max_digits=20, verbose_name='Value')),
                ('paid_value', models.DecimalField(decimal_places=2, default=0, max_digits=20, verbose_name='Paid Value')),
                ('final_value', models.DecimalField(decimal_places=2, default=0, max_digits=20, verbose_name='Final Value')),
                ('discount', models.DecimalField(decimal_places=2, default=0, max_digits=20, verbose_name='Discount')),
                ('is_paid', models.BooleanField(default=False, verbose_name='Is Paid')),
                ('printed', models.BooleanField(default=False, verbose_name='Printed')),
                ('additional_value', models.DecimalField(decimal_places=2, default=0.0, max_digits=15)),
                ('clean_value', models.DecimalField(decimal_places=2, default=0.0, max_digits=15)),
                ('taxes_modifier', models.CharField(choices=[('1', 13), ('2', 23), ('3', 24), ('4', 0)], default='1', max_length=1)),
                ('taxes', models.DecimalField(decimal_places=2, default=0.0, max_digits=15)),
                ('order_type', models.CharField(choices=[('1', 'Τιμολόγιο - Δελτίο Αποστολής'), ('2', 'Τιμολόγιο'), ('3', 'Δελτίο Απόστολης'), ('4', 'Εισαγωγή Αποθήκης'), ('5', 'Εξαγωγή Αποθήκης')], default=1, max_length=1)),
                ('paycheck', models.ManyToManyField(to='catalogue.VendorPaycheck')),
                ('payment_method', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='site_settings.PaymentMethod', verbose_name='PaymentMethod')),
                ('user_account', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
                ('vendor', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='vendor_orders', to='catalogue.Vendor')),
            ],
            options={
                'verbose_name_plural': '1. Warehouse Invoice',
                'ordering': ['-date_expired'],
            },
        ),
        migrations.CreateModel(
            name='InvoiceImage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(null=True, upload_to=warehouse.models.upload_image, validators=[warehouse.models.validate_file])),
                ('is_first', models.BooleanField(default=True)),
                ('order_related', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='warehouse.Invoice')),
            ],
        ),
        migrations.CreateModel(
            name='InvoiceOrderItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('edited', models.DateTimeField(auto_now=True)),
                ('qty', models.PositiveIntegerField(default=1)),
                ('value', models.DecimalField(decimal_places=2, default=0.0, max_digits=20)),
                ('discount_value', models.IntegerField(default=0, verbose_name='Discount %')),
                ('final_value', models.DecimalField(decimal_places=2, default=0, max_digits=20)),
                ('sku', models.CharField(max_length=150, null=True)),
                ('unit', models.CharField(choices=[('1', 'Τεμάχια'), ('2', 'Κιλά'), ('3', 'Κιβώτια')], default='1', max_length=1)),
                ('total_clean_value', models.DecimalField(decimal_places=2, default=0, max_digits=15)),
                ('total_final_value', models.DecimalField(decimal_places=2, default=0, max_digits=14)),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='order_items', to='warehouse.Invoice')),
                ('product', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='invoice_products', to='catalogue.Product')),
            ],
        ),
        migrations.CreateModel(
            name='Occupation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('active', models.BooleanField(default=True)),
                ('title', models.CharField(max_length=64, verbose_name='Occupation')),
                ('notes', models.TextField(blank=True, null=True, verbose_name='Notes')),
                ('balance', models.DecimalField(decimal_places=2, default=0, max_digits=50, verbose_name='Balance')),
                ('store', models.ManyToManyField(blank=True, null=True, to='site_settings.Store')),
            ],
            options={
                'verbose_name': 'Occupation',
                'verbose_name_plural': '3. Occupations',
            },
        ),
        migrations.CreateModel(
            name='Payroll',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uid', models.UUIDField(default=uuid.uuid4, editable=False, verbose_name='Friendly ID')),
                ('title', models.CharField(max_length=150, verbose_name='Title')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('edited', models.DateTimeField(auto_now=True)),
                ('notes', models.TextField(blank=True, null=True, verbose_name='Notes')),
                ('date_expired', models.DateField(default=django.utils.timezone.now, verbose_name='Date expired')),
                ('value', models.DecimalField(decimal_places=2, default=0, max_digits=20, verbose_name='Value')),
                ('taxes', models.DecimalField(decimal_places=2, default=0, max_digits=20, verbose_name='Taxes')),
                ('paid_value', models.DecimalField(decimal_places=2, default=0, max_digits=20, verbose_name='Paid Value')),
                ('final_value', models.DecimalField(decimal_places=2, default=0, max_digits=20, verbose_name='Final Value')),
                ('discount', models.DecimalField(decimal_places=2, default=0, max_digits=20, verbose_name='Discount')),
                ('is_paid', models.BooleanField(default=False, verbose_name='Is Paid')),
                ('printed', models.BooleanField(default=False, verbose_name='Printed')),
                ('category', models.CharField(choices=[('1', 'Μισθός'), ('2', 'ΙΚΑ'), ('3', 'ΑΣΦΑΛΙΣΤΙΚΕΣ ΕΙΣΦΟΡΕΣ'), ('4', 'ΗΜΕΡΟΜΗΣΘΙΟ'), ('5', 'ΕΡΓΟΣΗΜΟ'), ('6', 'ΔΩΡΟ')], default='1', max_length=1)),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='person_invoices', to='warehouse.Employee', verbose_name='Employee')),
                ('payment_method', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='site_settings.PaymentMethod', verbose_name='PaymentMethod')),
                ('user_account', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Εντολή Πληρωμής',
                'verbose_name_plural': '2. Μισθόδοσία',
                'ordering': ['is_paid', '-date_expired'],
            },
        ),
        migrations.AddField(
            model_name='employee',
            name='occupation',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='employees', to='warehouse.Occupation', verbose_name='Occupation'),
        ),
        migrations.AlterUniqueTogether(
            name='invoiceorderitem',
            unique_together={('order', 'product')},
        ),
        migrations.AlterUniqueTogether(
            name='billcategory',
            unique_together={('store', 'title')},
        ),
    ]
