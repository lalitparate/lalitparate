#!/usr/bin/env python2.6
"""
This module is simply a front-end for :mod:`django.core.management`, passing :mod:`web.settings` to :func:`django.core.management.execute_manager`.
"""
from django.core.management import setup_environ, ManagementUtility
import imp
import os
import sys

try:
    imp.find_module('settings')  # Assumed to be in the same directory.
except ImportError:
    sys.stderr.write("Error: Can't find the file 'settings.py' in the directory containing %r. It appears you've customized things.\nYou'll have to run django-admin.py, passing it your settings module.\n" % __file__)
    sys.exit(1)

import settings
# from scripts.one_time_operations import create_views_on_piggy_back_keys
# Not useful as most of the time developers doesn't have Search Aggregtation's Backend Schema Ready - causes runtime failures


def create_schema_before_syncdb(**options):
    from django.db import connections, transaction
    db = options.get('database') or 'default'
    connection = connections[db]
    cursor = connection.cursor()

    try:
        print "Creating schema sdmagg"
        cursor.execute('CREATE SCHEMA sdmagg;')
        transaction.commit_unless_managed(using=db)
    except:
        transaction.rollback_unless_managed(using=db)


def execute_manager(settings_mod, argv=None):
    """
    Like execute_from_command_line(), but for use by manage.py, a
    project-specific django-admin.py utility.
    """
    setup_environ(settings_mod)
    # Set up Green Plum Database Features
    execfile(os.path.abspath(os.path.join(os.path.dirname(__file__), 'greenplum_monkey_patch.py')))
    if os.getpid() - os.getppid() == 1:  # Let Run-Server print the notifications once on the console
        sys.stdout.write("Applying Green plum Monkey Patch...Success\n")
        sys.stdout.flush()
    # END Set up Green Plum Database Features
    utility = ManagementUtility(argv)
    if 'syncdb' in sys.argv:
        from django import get_version
        from django.core.management import LaxOptionParser
        from django.core.management.commands import syncdb
        parser = LaxOptionParser(usage="%prog subcommand [options] [args]",
                                 version=get_version(),
                                 option_list=syncdb.Command.option_list)
        options = parser.parse_args(sys.argv)[0]
        create_schema_before_syncdb(**options.__dict__)
        # create_views_on_piggy_back_keys()
    utility.execute()


if __name__ == "__main__":
    execute_manager(settings)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
