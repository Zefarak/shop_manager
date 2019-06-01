from django.urls import path
from .views import (DashboardView, OrderListView, SellListView, CreateOrderView, OrderUpdateView, delete_order,
                    check_product, add_to_order_with_attr, order_item_edit_with_attr,
                    CostumerCreateView, CostumerListView, CostumerUpdateView, delete_costumer_view, CostumerAccountCardView
                    )
from .ajax_views import ajax_order_item, ajax_search_products, ajax_add_product, ajax_costumers_report, ajax_search_costumers, ajax_costumer_order_pay_view
from .views_actions import auto_create_retail_order, done_order_view, quick_pay_costumer_view, create_copy_order
from .autocomplete_widget import ProfileAutoComplete

app_name = 'point_of_sale'

urlpatterns = [
    path('', DashboardView.as_view(), name='home'),
    path('order-list/', OrderListView.as_view(), name='order_list'),
    path('eshop-orders/', SellListView.as_view(), name='sell_list'),
    path('order-create/', CreateOrderView.as_view(), name='order_create'),
    path('order-detail/<int:pk>/', OrderUpdateView.as_view(), name='order_detail'),
    path('order-detail/<int:pk>/delete/', delete_order, name='delete_order'),
    path('order/check-add/<int:pk>/<int:dk>/', check_product, name='check_add'),
    path('order/add-product-attr/<int:pk>/<int:dk>/', add_to_order_with_attr, name='add_to_order_attr'),
    path('order/edit-order-item-with-att/<int:pk>/', order_item_edit_with_attr, name='edit_order_item_attr'),
    path('copy-order/<int:pk>/', create_copy_order, name='copy_order'),

    #  ajax calls
    path('order/ajax/edit-order-item/<slug:action>/<int:pk>/', ajax_order_item, name='ajax_order_item_edit'),
    path('ajax/search-items/<int:pk>/', ajax_search_products, name='ajax_search'),
    path('ajax/search-items/<int:pk>/<int:dk>/', ajax_add_product, name='ajax_add_product'),
    path('ajax/costumer-pay-order/<int:pk>/', ajax_costumer_order_pay_view, name='ajax_costumer_pay_order'),
    path('ajax/costumer/report', ajax_costumers_report, name='ajax_costumer_report'),
    path('ajax/costumer/search/', ajax_search_costumers, name='ajax_costumer_search'),

    #  actions
    path('action/auto-create-order/<slug:action>/', auto_create_retail_order, name='auto_create_order'),

    path('action/order-done/<int:pk>/<slug:action>/', done_order_view, name='action_order_done'),
    path('autocomplete/profile/', ProfileAutoComplete.as_view(), name='autocomplete_profile'),

    # costumer views
    path('costumer/list/', CostumerListView.as_view(), name='costumer_list_view'),
    path('costumer/create/', CostumerCreateView.as_view(), name='costumer_create_view'),
    path('costumer/detail/<int:pk>/', CostumerUpdateView.as_view(), name='costumer_update_view'),
    path('costumer/delete/<int:pk>/', delete_costumer_view, name='costumer_delete_view'),
    path('costumer/account-card/<int:pk>/', CostumerAccountCardView.as_view(), name='costumer_account_card'),
    path('costumer/quick/pay/<int:pk>/', quick_pay_costumer_view, name='costumer_pay'),



]