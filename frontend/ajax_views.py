from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.http import JsonResponse
from voucher.models import Voucher

from cart.tools import check_or_create_cart

def ajax_delete_voucher(request, pk):
    voucher = get_object_or_404(Voucher, id=pk)
    cart = check_or_create_cart(request)
    cart.vouchers.remove(voucher)
    cart.save()
    data = dict()
    cart.refresh_from_db()
    data['result'] = render_to_string(template_name='',
                                      request=request,
                                      context = {
                                          'cart': cart
                                      })
    return JsonResponse(data)