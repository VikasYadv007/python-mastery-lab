"""Owner-only account recovery. Run locally, NEVER in a public app browser.

Windows PowerShell example:
  $env:DATABASE_URL = 'postgresql://...'
  python manage_users.py reset student
"""
import argparse
import getpass
import os
import sys

import cloud_storage as cloud
import quiz_core as core


def main() -> None:
    cli = argparse.ArgumentParser(description='Privately create or reset a hosted learner password')
    cli.add_argument('action', choices=['create', 'reset'])
    cli.add_argument('username')
    args = cli.parse_args()
    if not os.environ.get('DATABASE_URL'):
        sys.exit('Set DATABASE_URL in your local terminal first. Never commit credentials.')
    cloud.configure(os.environ['DATABASE_URL'])
    core.init_db()
    pw = getpass.getpass('New password (minimum 10 characters): ')
    confirm = getpass.getpass('Confirm password: ')
    if pw != confirm:
        sys.exit('Passwords do not match.')
    if args.action == 'create':
        result = core.register_user(args.username, pw)
        print('Created account:', result)
    else:
        core.reset_user_password(args.username, pw)
        print('Updated password for:', args.username)


if __name__ == '__main__':
    main()
