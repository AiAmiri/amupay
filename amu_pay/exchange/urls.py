from django.urls import path
from .views import (
    ExchangeTransactionListView,
    ExchangeTransactionCreateView,
    ExchangeTransactionDetailView,
    CustomerExchangeListView
)

app_name = 'exchange'

urlpatterns = [
    # Public endpoint - Get exchanges by customer phone number
    path('customer/', CustomerExchangeListView.as_view(), name='customer_exchange_list'),
    
    # Exchange transaction management
    path('', ExchangeTransactionListView.as_view(), name='exchange_list'),
    path('create/', ExchangeTransactionCreateView.as_view(), name='exchange_create'),
    path('<int:exchange_id>/', ExchangeTransactionDetailView.as_view(), name='exchange_detail'),
]
