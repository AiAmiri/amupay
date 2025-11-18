from django.urls import path
from .views import (
    SarafBalanceListView,
    SarafBalanceDetailView,
    DeleteSarafBalanceView
)

app_name = 'saraf_balance'

urlpatterns = [
    # List of Saraf balances
    path('', SarafBalanceListView.as_view(), name='balance_list'),
    
    # Details of balance for a specific currency
    path('<str:currency_code>/', SarafBalanceDetailView.as_view(), name='balance_detail'),
    
    # Delete balance for a specific currency
    path('<str:currency_code>/delete/', DeleteSarafBalanceView.as_view(), name='delete_balance'),
]