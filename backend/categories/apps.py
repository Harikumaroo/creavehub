from django.apps import AppConfig


class CategoriesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "categories"
    verbose_name = "Categories"

    def ready(self):
        import categories.signals  # noqa: F401