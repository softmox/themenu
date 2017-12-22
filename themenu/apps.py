from django.apps import AppConfig


class ThemenuConfig(AppConfig):
    name = 'themenu'

    def ready(self):
        from themenu import signals
