from rest_framework import generics
import django_filters.rest_framework
from rest_framework import permissions, pagination
from django.middleware.csrf import get_token
from rest_framework.response import Response
from rest_framework.views import APIView
from ..models import Order, OrderItem
from .serializers import OrderSerializer, OrderItemSerializer


class OrderListApiView(generics.ListCreateAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated, ]
    queryset = Order.objects.all()


class OrderCreateApiView(generics.CreateAPIView):
    serializer_class = OrderSerializer
    queryset = Order.objects.all()
    permission_classes = [permissions.IsAuthenticated, ]


class OrderUpdateApiView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = OrderSerializer
    queryset = Order.objects.all()
    permission_classes = [permissions.IsAuthenticated, ]


class OrderItemListCreateApiView(generics.ListCreateAPIView):
    serializer_class = OrderItemSerializer
    queryset = OrderItem.objects.all()
    permission_classes = [permissions.IsAuthenticated, ]
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend, )
    filterset_fields = ('order', 'title', )


class OrderItemUpdateApiView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = OrderItemSerializer
    queryset = OrderItem.objects.all()
    permission_classes = [permissions.IsAuthenticated, ]


class TokenApiView(APIView):
    permission_classes = (permissions.IsAuthenticated,)             # <-- And here

    def get(self, request):
        content = {'token': get_token(request)}
        return Response(content)