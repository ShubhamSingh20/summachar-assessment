from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.apps import apps

class Command(BaseCommand):
    help = 'clear all the data within db'

    
    def boolean_input(self, question, default=None):
        result = input("%s " % question)
        if not result and default is not None:
            return default
        while len(result) < 1 or result[0].lower() not in "yn":
            result = input("Please answer yes or no: ")
        return result[0].lower() == "y"

    def handle(self, *args, **options):
        if not settings.DEBUG:
            raise CommandError("dbfersh command can only be run with `DEBUG` set to `True`")
        
        if not self.boolean_input('Are you sure you want to clear db ?'):
            self.stdout.write(self.style.NOTICE('Operation aborted'))
            return

        public_model = apps.get_models()

        for model in public_model:
            model.objects.all().delete()

        self.stdout.write(self.style.SUCCESS('All the tables cleared!'))
