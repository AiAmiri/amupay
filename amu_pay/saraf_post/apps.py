from django.apps import AppConfig


class SarafPostConfig(AppConfig):
    """
    Configuration for the saraf_post app
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'saraf_post'
    verbose_name = 'Exchange House Posts'
    
    def ready(self):
        """
        Import signal handlers when the app is ready
        """
        try:
            import saraf_post.signals
        except ImportError:
            pass