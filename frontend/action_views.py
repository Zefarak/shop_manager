from django.shortcuts import get_object_or_404, HttpResponseRedirect, reverse
from cart.tools import check_or_create_cart
from voucher.models import Voucher


def remove_voucher_from_cart_view(request, pk):
    voucher = get_object_or_404(Voucher, id=pk)
    cart = check_or_create_cart(request)
    cart.vouchers.remove(voucher)
    cart.save()
    return HttpResponseRedirect(reverse('cart_page'))