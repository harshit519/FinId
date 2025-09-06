from django.apps import AppConfig


class KycConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'kyc'

    def ready(self):
        # Import signals to auto-create user profiles on user creation
        try:
            import kyc.signals  # noqa: F401
        except Exception:
            pass
