#!/usr/bin/env python
"""Script to create an admin user."""
import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'apps'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from apps.users.services import UserService
from services.cosmos_db import CosmosDBService


def main():
    email = input('Admin email: ')
    password = input('Admin password: ')
    display_name = input('Display name: ')

    if UserService.exists_by_email(email):
        print(f'User with email {email} already exists.')
        update = input('Update to admin? (y/n): ')
        if update.lower() == 'y':
            user = UserService.get_by_email(email)
            user_dict = user.to_dict()
            user_dict['role'] = 'admin'
            CosmosDBService.upsert('users', user_dict)
            print(f'User {email} updated to admin.')
        return

    user = UserService.create(
        email=email,
        password=password,
        display_name=display_name,
    )

    user_dict = user.to_dict()
    user_dict['role'] = 'admin'
    CosmosDBService.upsert('users', user_dict)

    print(f'Admin user created: {email}')


if __name__ == '__main__':
    main()
