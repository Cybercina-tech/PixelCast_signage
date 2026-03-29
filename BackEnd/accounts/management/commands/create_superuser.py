"""
Management command to create a superuser.

This is a convenience command that creates a Developer (superuser) account.

Usage:
    python manage.py create_superuser
"""

from django.core.management.base import BaseCommand
from accounts.management.commands.create_user import Command as CreateUserCommand


class Command(BaseCommand):
    help = 'Create a Developer superuser (convenience wrapper for create_user)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            help='Username for the superuser'
        )
        parser.add_argument(
            '--email',
            type=str,
            help='Email address for the superuser'
        )

    def handle(self, *args, **options):
        username = options.get('username')
        email = options.get('email')
        
        if not username:
            username = input('Username: ')
        if not email:
            email = input('Email: ')
        
        # Create superuser directly
        from django.contrib.auth.password_validation import validate_password
        from django.core.exceptions import ValidationError
        import getpass
        from accounts.models import User
        
        # Check if user already exists
        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.ERROR(f'User with username "{username}" already exists.'))
            return
        
        if User.objects.filter(email=email.lower()).exists():
            self.stdout.write(self.style.ERROR(f'User with email "{email}" already exists.'))
            return
        
        # Get password
        password = getpass.getpass('Password: ')
        password_confirm = getpass.getpass('Password (again): ')
        
        if password != password_confirm:
            self.stdout.write(self.style.ERROR('Passwords do not match.'))
            return
        
        if not password:
            self.stdout.write(self.style.ERROR('Password cannot be empty.'))
            return
        
        # Validate password
        try:
            validate_password(password)
        except ValidationError as e:
            self.stdout.write(self.style.ERROR(f'Password validation failed: {"; ".join(e.messages)}'))
            return
        
        # Create user
        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                role='Developer',
                is_active=True,
                is_staff=True,
                is_superuser=True
            )
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully created Developer user "{username}"'
                )
            )
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error creating user: {str(e)}'))
