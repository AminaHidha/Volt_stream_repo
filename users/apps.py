from django.apps import AppConfig


class UsersConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "users"

    def ready(self):
        """
        Django calls this when the app is ready.
        We import signals here so they get registered automatically.
        """
        import users.signals
