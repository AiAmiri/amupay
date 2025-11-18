from django.urls import path
from .views import (
    ExchangeTransactionListView,
    ExchangeTransactionCreateView,
    ExchangeTransactionDetailView
)

app_name = 'exchange'

urlpatterns = [
    # Exchange transaction management
    path('', ExchangeTransactionListView.as_view(), name='exchange_list'),
    path('create/', ExchangeTransactionCreateView.as_view(), name='exchange_create'),
    path('<int:exchange_id>/', ExchangeTransactionDetailView.as_view(), name='exchange_detail'),
]
