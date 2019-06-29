from django.urls import path

from .views import VoucherListView

app_name= 'vouchers'

urlpatterns = [
    path('list/', VoucherListView.as_view(), name='voucher_list'),
]