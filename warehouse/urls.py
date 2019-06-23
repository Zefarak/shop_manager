from django.urls import path
from .views import (
    WarehouseDashboard, BillingHomepageView,
    CreateBillingInvoiceView, BillInvoiceEditView, quick_billing_pay,
    delete_bill_invoice_view, CreateBillingCategoryView, EditBillingCategoryView, delete_bill_category_view,
    TranscationHomepage, InvoiceBillingCreateView, BillCategoryListView, create_bill_copy,
    GenericExpenseListView, GenericExpenseCreateView, GenericExpenseUpdateView, delete_generic_expense,
    GenericExpenseCateListView, GenericExpenseCateUpdateView, GenericExpenseCateCreateView, delete_generic_expense_category,
    GenericExpensePersonListView, GenericExpensePersonCreateView, GenericExpensePersonUpdateView, delete_generic_expense_person,
    )

from .invoice_views import (WarehouseOrderList, create_warehouse_order_view, UpdateWarehouseOrderView,
                            CreateOrderItem, check_if_product_have_attr_view, UpdateInvoiceOrderItem,
                            delete_warehouse_order_item_view,
                            VendorListView, VendorCreateView, VendorUpdateView, delete_vendor,
                            CreateInvoiceImageView, UpdateInvoiceImageView, delete_invoice_image_view,

                            create_order_item_with_attribute_view,
                            create_copy_invoice_view, delete_warehouse_order_view
                            )

from .payroll_views import (PayrollListView, EmployeeListView, EmployeeCreateView, EmployeeEditView, delete_employee,
                            OccupationCreateView, OccupationListView, OccupationUpdateView, delete_occupation,
                            PayrollCreateView, payroll_quick_pay, PayrollUpdateView, delete_payroll
                            )
from .ajax_calls import (ajax_paycheck_actions, ajax_calculate_value, ajax_search_products, popup_new_bill,
                         popup_employee, popup_occupation, popup_generic_category, popup_generic_person,
                         ajax_add_attr_to_invoice_view, ajax_edit_invoice_attr_view )

from .report_views import report_generic_expenses_view, report_billing_view
from .invoice_payments_views import (PayCheckListView, PaycheckDetailView, PaycheckCreateView, delete_paycheck,
                                     InvoicePaymentListView, InvoicePaymentCreateView, InvoicePaymentUpdateView
                                     )
from .pdf_views import download_cv_pdf
from .autocomplete_widgets import EmployeeAutocomplete

app_name = 'warehouse'

urlpatterns = [
    path('', WarehouseDashboard.as_view(), name='dashboard'),

    # invoices
    path('invoices/', WarehouseOrderList.as_view(), name='invoices'),
    path('invoice/delete/<int:pk>/', delete_warehouse_order_view, name='invoice_delete'),
    path('create-invoice/', create_warehouse_order_view, name='create_invoice'),
    path('invoices/update/<int:pk>/', UpdateWarehouseOrderView.as_view(), name='update_order'),
    path('invoice/order-item/check/<int:pk>/<int:dk>/', check_if_product_have_attr_view, name='order_item_check'),
    path('invoice/order-item-with_attr/<int:pk>/<int:dk>/', create_order_item_with_attribute_view, name='create_order_item_with_attr'),
    path('invoice/order-item/create/<int:pk>/<int:dk>/', CreateOrderItem.as_view(), name='create-order-item'),
    path('invoices/order-item/update/<int:pk>/', UpdateInvoiceOrderItem.as_view(), name='order-item-update'),
    path('invoices/order-item/delete/<int:pk>/', delete_warehouse_order_item_view, name='order-item-delete'),
    
    path('invoice/<int:pk>/', create_copy_invoice_view, name='invoice_create_copy'),

    # ajax urls
    path('ajax/calculate/<slug:question>/', ajax_calculate_value, name='ajax_invoice'),
    path('ajax/paycheck-actions/<slug:question>/', ajax_paycheck_actions, name='ajax_paycheck_actions'),
    path('ajax/search-products/<int:pk>/', ajax_search_products, name='ajax_ware_search'),
    path('popup/new-bill-category/', popup_new_bill, name='popup-new-bill'),
    path('popup/new-employee/', popup_employee, name='popup-employee'),
    path('popup/new-occupation/', popup_occupation, name='popup-occupation'),
    path('auto-complete-employee/', EmployeeAutocomplete.as_view(), name='auto-employee'),
    path('popup/new-generic-category/', popup_generic_category, name='popup-generic-category'),
    path('popup/new-generic-person/', popup_generic_person, name='popup-generic-person'),
    path('add-attr-to-invoice/<int:pk>/<int:dk>', ajax_add_attr_to_invoice_view, name='add_attr_to_invoice'),
    path('ajax/edit-order-item-with-attr/<int:pk>/', ajax_edit_invoice_attr_view, name='ajax_edit_attr_invoice'),

    #  reports
    path('report/generic-expenses/', report_generic_expenses_view, name='report_generic_expenses'),
    path('report/billing/', report_billing_view, name='report_billing'),


    path('invoice/order-image/create/<int:pk>/', CreateInvoiceImageView.as_view(), name='create-order-image'),
    path('invoices/order-image/update/<int:pk>/', UpdateInvoiceImageView.as_view(), name='update-order-image'),
    path('invoices/order-image/delete/<int:pk>/', delete_invoice_image_view, name='delete-order-image'),

    path('paychecks/', PayCheckListView.as_view(), name='paychecks'),
    path('paychecks/<int:pk>/', PaycheckDetailView.as_view(), name='paycheck_detail'),
    path('paychecks/create/', PaycheckCreateView.as_view(), name='paycheck_create'),
    path('paychecks/delete/<int:pk>/', delete_paycheck, name='paycheck_delete'),

    path('paychecks/invoice/list/<int:pk>/', InvoicePaymentListView.as_view(), name='invoice_paycheck_list'),
    path('paycheck/invoice/create/<int:pk>/', InvoicePaymentCreateView.as_view(), name='invoice_paycheck_create'),
    path('paycheck/invoice/edit/<int:pk>/', InvoicePaymentUpdateView.as_view(), name='invoice_paycheck_update'),


    path('vendors/', VendorListView.as_view(), name='vendors'),
    path('vendor/<int:pk>/', VendorUpdateView.as_view(), name='vendor_detail'),
    path('vendors/create/', VendorCreateView.as_view(), name='vendor_create'),
    path('vendor/delete/<int:pk>/', delete_vendor, name='vendor_delete'),

    path('transcation/homepage/', TranscationHomepage.as_view(), name='transcation_homepage'),
    path('billing-view/', BillingHomepageView.as_view(), name='billing_view'),
    path('billing-category-view/', BillCategoryListView.as_view(), name='billing_category_view'),
    path('billing-create-view/<int:pk>/', CreateBillingInvoiceView.as_view(), name='bill_invoice_create_category'),
    path('billing-create/', InvoiceBillingCreateView.as_view(), name='billing_invoice_create_view'),

    path('create-copy-for-billing/<int:pk>/<slug:date_range>/', create_bill_copy, name='bill-copy'),

    path('billing-invoice-edit-view/<int:pk>/', BillInvoiceEditView.as_view(), name='bill_invoice_edit_view'),
    path('billing-invoice-edit-view-pay/<int:pk>/', quick_billing_pay, name='quick_pay_invoice'),
    path('billing-invoice-delete-view/<int:pk>/', delete_bill_invoice_view, name='bill_invoice_delete_view'),

    path('billing-category-create-view/', CreateBillingCategoryView.as_view(), name='billing_category_create_view'),
    path('billing-category-edit-view/<int:pk>/', EditBillingCategoryView.as_view(), name='bill_category_edit_view'),
    path('billing-category-delete-view/<int:pk>/', delete_bill_category_view, name='bill_category_delete_view'),

    # payroll views
    path('payroll/homepage/', PayrollListView.as_view(), name='payroll_homepage'),
    path('payroll/employee-list/', EmployeeListView.as_view(), name='payroll_employee'),
    path('payroll/employee-create/', EmployeeCreateView.as_view(), name='payroll_employee_create'),
    path('payroll/employee-edit/<int:pk>/', EmployeeEditView.as_view(), name='payroll_employee_edit'),
    path('payroll/employee-delete/<int:pk>/', delete_employee, name='payroll_employee_delete'),

    path('payroll/occupation-list/', OccupationListView.as_view(), name='occupation_list'),
    path('payroll/occupation-create/', OccupationCreateView.as_view(), name='occupation_create'),
    path('payroll/occupation-edit/<int:pk>/', OccupationUpdateView.as_view(), name='occupation_edit'),
    path('payroll/occupation-delete/<int:pk>/', delete_occupation, name='occupation_delete'),

    path('payroll/create/', PayrollCreateView.as_view(), name='payroll_create'),
    path('payroll/quick-pay/<int:pk>/', payroll_quick_pay, name='payroll_quick_pay'),
    path('payroll/edit/<int:pk>/', PayrollUpdateView.as_view(), name='payroll_edit'),
    path('payroll/delete/<int:pk>/', delete_payroll, name='payroll_delete'),

    path('generic-expense/list/', GenericExpenseListView.as_view(), name='generic-expense-list'),
    path('generic-expense/create/', GenericExpenseCreateView.as_view(), name='generic-expense-create'),
    path('generic-expense/edit/<int:pk>/', GenericExpenseUpdateView.as_view(), name='generic-expense-edit'),
    path('generic-expense/delete/<int:pk>/', delete_generic_expense, name='generic-expense-delete'),

    path('generic-expense-cate/list/', GenericExpenseCateListView.as_view(), name='generic-expense-cate-list'),
    path('generic-expense-cate/create/', GenericExpenseCateCreateView.as_view(), name='generic-expense-cate-create'),
    path('generic-expense-cate/edit/<int:pk>/', GenericExpenseCateUpdateView.as_view(), name='generic-expense-cate-edit'),
    path('generic-cate/delete/<int:pk>/', delete_generic_expense_category, name='generic-expense-cate-delete'),

    path('generic-expense-person/list/', GenericExpensePersonListView.as_view(), name='generic-expense-person-list'),
    path('generic-expense-person/create/', GenericExpensePersonCreateView.as_view(), name='generic-expense-person-create'),
    path('generic-expense-person/edit/<int:pk>/', GenericExpensePersonUpdateView.as_view(), name='generic-expense-person-edit'),
    path('generic-person/delete/<int:pk>/', delete_generic_expense_person, name='generic-expense-person-delete'),

    #  report pdfs
    path('pdf-create/<slug:slug>/', download_cv_pdf, name='pdf_create')

    ]