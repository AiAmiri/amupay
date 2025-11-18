from django.urls import path
from .views import (
    AvailableCurrenciesView,
    SarafSupportedCurrenciesView
)

app_name = 'currency'

urlpatterns = [
    # List of all available currencies in the system
    path('available/', AvailableCurrenciesView.as_view(), name='available_currencies'),
    
    # Management of Saraf supported currencies
    path('supported/', SarafSupportedCurrenciesView.as_view(), name='supported_currencies'),
]
