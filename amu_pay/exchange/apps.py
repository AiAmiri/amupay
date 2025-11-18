from django.apps import AppConfig


class ExchangeConfig(AppConfig):
    """
    Configuration for the exchange app
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'exchange'
    verbose_name = 'Exchange Transactions'
    
    def ready(self):
        """
        Import signal handlers when the app is ready
        """
        try:
            import exchange.signals
        except ImportError:
            pass
