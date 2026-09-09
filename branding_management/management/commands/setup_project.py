# branding_management/management/commands/setup_project.py
from django.core.management.base import BaseCommand
from django.core.management import call_command

class Command(BaseCommand):
    help = 'Setup project with sample data'

    def handle(self, *args, **kwargs):
        self.stdout.write('Creating superuser...')
        call_command('createsuperuser')
        
        self.stdout.write('Creating sample data...')
        call_command('create_sample_data')
        
        self.stdout.write(self.style.SUCCESS('✅ Project setup complete!'))