from django.core.management.base import BaseCommand, CommandError
from optparse import make_option
from corehq.apps.api.models import ApiUser
from corehq.apps.kookoo.views import PERMISSION_KOOKOO
from corehq.apps.megamobile.views import PERMISSION_MEGAMOBILE
from corehq.apps.sislog.views import PERMISSION_SISLOG
from corehq.apps.tropo.views import PERMISSION_TROPO
from corehq.apps.twilio.views import PERMISSION_TWILIO
from corehq.apps.unicel.views import PERMISSION_UNICEL
from corehq.apps.yo.views import PERMISSION_YO
import os

class Command(BaseCommand):
    args = ""
    help = "Create api keys used by 3rd-party gateways."

    def handle(self, *args, **options):
        print "Creating API Keys for all gateways..."
        for permission in [
            PERMISSION_KOOKOO,
            PERMISSION_MEGAMOBILE,
            PERMISSION_SISLOG,
            PERMISSION_TROPO,
            PERMISSION_TWILIO,
            PERMISSION_UNICEL,
            PERMISSION_YO,
        ]:
            api_key = os.urandom(16).encode('hex')
            u = ApiUser.create(api_key, api_key, permissions=[permission])
            u.save()
            print "%s: %s" % (permission, api_key)

