from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command

class Command(BaseCommand):
    help = '''
        Creates any new migrations and migrates the database.
    '''

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Are you sure you wish to migrate the DB (Y/n)?'), ending=' ')
        response_migrate = raw_input().lower()
        if response_migrate == 'n':
            self.stdout.write(self.style.WARNING("...CANCELLED.\n"))
        else:
            self.stdout.write(self.style.SUCCESS("Updating migrations and migrating DB..."))

            call_command('makemigrations')
            call_command('migrate')

            self.stdout.write(self.style.SUCCESS('...DONE.\n'))
