from django.urls import path
from .views import (
    CreateCustomerAccountView,
    ListCustomerAccountsView,
    CustomerAccountDetailView,
    CustomerTransactionListView,
    PublicCustomerTransactionListView,
    PublicAllAccountsTransactionsView,
    CustomerBalanceListView,
    CustomerDepositView,
    CustomerWithdrawView,
    ExchangerTakeMoneyView,
    ExchangerGiveMoneyView,
    ExchangerBalanceView,
    CustomerWithdrawalAmountsView,
    CustomerDepositAmountsView,
    ExchangerGivenAmountsView,
    ExchangerTakenAmountsView,
)

urlpatterns = [
    # Customer Account Management
    path('create/', CreateCustomerAccountView.as_view(), name='create_customer_account'),
    path('list/', ListCustomerAccountsView.as_view(), name='list_customer_accounts'),
    path('<int:account_id>/', CustomerAccountDetailView.as_view(), name='customer_account_detail'),
    
    # Transaction Management
    path('<int:account_id>/transactions/', CustomerTransactionListView.as_view(), name='customer_transactions'),
    path('public/transactions/<str:phone>/', PublicCustomerTransactionListView.as_view(), name='public_customer_transactions'),
    path('public/all-accounts/<str:phone>/', PublicAllAccountsTransactionsView.as_view(), name='public_all_accounts_transactions'),
    
    # Balance Management
    path('<int:account_id>/balances/', CustomerBalanceListView.as_view(), name='customer_balances'),
    
    # Financial Operations
    path('<int:account_id>/deposit/', CustomerDepositView.as_view(), name='customer_deposit'),
    path('<int:account_id>/withdraw/', CustomerWithdrawView.as_view(), name='customer_withdraw'),
    path('<int:account_id>/take-money/', ExchangerTakeMoneyView.as_view(), name='exchanger_take_money'),
    path('<int:account_id>/give-money/', ExchangerGiveMoneyView.as_view(), name='exchanger_give_money'),
    
    # Exchanger Balance (with saraf impact)
    path('<int:account_id>/exchanger-balance/', ExchangerBalanceView.as_view(), name='exchanger_balance'),
    
    # Amount Summary Endpoints
    path('<int:account_id>/withdrawal-amounts/', CustomerWithdrawalAmountsView.as_view(), name='customer_withdrawal_amounts'),
    path('<int:account_id>/deposit-amounts/', CustomerDepositAmountsView.as_view(), name='customer_deposit_amounts'),
    path('<int:account_id>/given-amounts/', ExchangerGivenAmountsView.as_view(), name='exchanger_given_amounts'),
    path('<int:account_id>/taken-amounts/', ExchangerTakenAmountsView.as_view(), name='exchanger_taken_amounts'),
]
