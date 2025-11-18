from django.apps import AppConfig


class MsgConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'msg'
    verbose_name = 'Messaging System'
    
    def ready(self):
        # Import signal handlers if any
        pass