from rest_framework.serializers import ModelSerializer
from ..models import Order, OrderItem


class OrderSerializer(ModelSerializer):
    class Meta:
        model = Order
        fields = ['id', 'date_expired', 'status', 'order_type', 'costumer', 'tag_final_value', 'final_value']
