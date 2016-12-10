from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command

class Command(BaseCommand):
    help = '''
        Runs the server, similar to runserver.
    '''

    def handle(self, *args, **options):
        call_command('runserver')
