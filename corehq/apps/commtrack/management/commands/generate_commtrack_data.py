from django.core.management.base import BaseCommand
from corehq.apps.domain.models import Domain
from corehq.apps.commtrack.models import CommTrackUser, Product, StockState
from corehq.apps.locations.models import Location
from casexml.apps.stock.models import StockTransaction, StockReport
import timecop
from datetime import timedelta
import datetime
import time
from corehq.apps.commtrack import sms
import random


class Command(BaseCommand):
    args = '<domain>'

    def handle(self, *args, **options):
        location_count = 5
        num_days = 10

        try:
            domain = Domain.get_by_name(args[0])
        except IndexError:
            self.stderr.write('domain required\n')
            return
        except:
            self.stderr.write('domain not right\n')
            return

        if not domain.commtrack_enabled:
            self.stderr.write('domain not commtrack\n')
            return

        user = CommTrackUser.by_domain(domain.name)[0]

        # clear data!
        for product in Product.by_domain(domain.name):
            StockState.objects.filter(
                product_id=product._id
            ).delete()

            transactions = StockTransaction.objects.filter(
                product_id=product._id
            ).delete()

            # TODO delete reports
            # StockReport.objects.filter(
            # ).delete()

        if not list(Location.by_domain(domain.name)):
            for i in range(location_count):
                loc = Location(
                    site_code='loc%d' % (i),
                    name='Location %d' % (i),
                    domain=domain.name,
                    location_type='outlet', # don't hardcode me
                )

                loc.save()

        #for loc in Location.by_domain(domain.name):
        with timecop.travel(time.mktime((datetime.datetime.now() -
                timedelta(days=num_days)).timetuple())):
            sms.handle(
                user.get_verified_number(), 'soh pp 50 pq 50 pr 50'
            )


        for day_offset in range(num_days - 1, 0, -1):
            action = 'r' if random.random() < 0.5 else 'l'
            pp = int(random.random() * 10)
            pq = int(random.random() * 10)
            pr = int(random.random() * 10)
            with timecop.travel(time.mktime((datetime.datetime.now() -
                    timedelta(days=day_offset)).timetuple())):
                print 'datetime: ' + str(datetime.datetime.now())
                sms.handle(
                    user.get_verified_number(), 
                    '{act} pp {pp} pq {pq} pr {pr}'.format(act=action, pp=pp,
                        pq=pq, pr=pr)
                )

