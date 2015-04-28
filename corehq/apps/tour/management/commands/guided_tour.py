import json
import os
from django.core.management.base import LabelCommand, BaseCommand
from django.conf import settings
from dimagi.utils import gitinfo


class Command(BaseCommand):
    help = "Activates a guided tour for the specified user + tour slug"
    option_list = BaseCommand.option_list + (
        make_option('--remove-user', action='store_true',  default=False,
                    help='Remove the users specified from the DIMAGI_OPERATIONS_TEAM privilege'),
    )

    root_dir = settings.FILEPATH

    def handle(self, *args, **options):
        if len(args) < 2:
            self.stdout.write("Syntax is <user> <tour_slug>"
