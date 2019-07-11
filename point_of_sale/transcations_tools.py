from site_settings.constants import ORDER_TYPES

REMOVE_QTY_TYPES = ['r', 'e', 'wr']
ADD_QTY_TYPES = ['b', 'c', 'wa']


def transcation_movement(product, order_type, qty):
    if order_type in REMOVE_QTY_TYPES:
        product.qty -= qty
    if order_type in ADD_QTY_TYPES:
        product.qty += qty
    product.save()


def update_transcation_movement(product, order_type, old_qty, new_qty):
    if order_type in REMOVE_QTY_TYPES:
        product.qty += old_qty
        product.qty -= new_qty
    if order_type in ADD_QTY_TYPES:
        product.qty -= old_qty
        product.qty += new_qty
    product.save()



def upgrade_tranascation_on_delete(product, order_type, qty):
    if order_type in REMOVE_QTY_TYPES:
        product.qty += qty
    if order_type in ADD_QTY_TYPES:
        product.qty -= qty
    product.save()