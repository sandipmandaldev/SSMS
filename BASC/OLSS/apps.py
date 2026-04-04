from django.apps import AppConfig

class OlssConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'OLSS'   # এটা তোমার app folder এর নামের সাথে same হতে হবে

    def ready(self):
        from . import signals   # এখানে relative import ব্যবহার করো