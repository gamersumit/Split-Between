from django.apps import AppConfig


class ExpenseConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'group'

    def ready(self):
        import group.signals
        