from django.urls import path
from .views import (
    CreateTransactionView,
    TransactionListView,
    TransactionDetailView,
    DeleteTransactionView
)

app_name = 'transaction'

urlpatterns = [
    # Create new transaction
    path('create/', CreateTransactionView.as_view(), name='create_transaction'),
    
    # List of transactions
    path('', TransactionListView.as_view(), name='transaction_list'),
    
    # Transaction details
    path('<int:transaction_id>/', TransactionDetailView.as_view(), name='transaction_detail'),
    
    # Delete transaction
    path('<int:transaction_id>/delete/', DeleteTransactionView.as_view(), name='delete_transaction'),
]
