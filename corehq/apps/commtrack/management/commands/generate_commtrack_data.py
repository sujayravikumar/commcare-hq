from django.core.management.base import BaseCommand
from corehq.apps.domain.models import Domain
from corehq.apps.commtrack.models import (
    Product,
    StockState,
    SupplyPointCase,
    CommtrackConfig,
    ConsumptionConfig
)
from corehq.apps.locations.models import Location
from corehq.apps.locations.schema import LocationType
from casexml.apps.stock.models import StockTransaction, StockReport
import timecop
from datetime import timedelta
import datetime
import time
from corehq.apps.commtrack import sms
import random
from corehq.apps.users.models import CommCareUser
from random import randint
from freezegun import freeze_time



class Command(BaseCommand):
    args = '<domain>'

    def handle(self, *args, **options):
        location_count = 5
        num_days = 10
        num_top_level_locs = 1
        num_mid_level_locs = 3
        num_bottom_level_locs = 10

        # CONFIGURE DOMAIN
        try:
            domain = Domain.get_or_create_with_name(
                name=args[0],
                is_active=True,
                secure_submissions=False
            )
        except IndexError:
            self.stderr.write('Must specify domain name\n')
            return
        except:
            self.stderr.write('Unknown error creating or fetching domain\n')
            return

        if not domain.commtrack_enabled:
            domain.commtrack_enabled = True
            domain.locations_enabled = True

        domain.save()

        # CONFIGURE SETTINGS
        ct_settings = CommtrackConfig.for_domain(domain.name)
        ct_settings.consumption_config = ConsumptionConfig(
            min_transactions=3,
            min_window=3,
            optimal_window=6,
        )
        ct_settings.use_auto_consumption = True
        ct_settings.save()
        domain.location_types = [
            LocationType(
                name='state',
                allowed_parents=[''],
                administrative=True
            ),
            LocationType(
                name='village',
                allowed_parents=['state'],
                administrative=True
            ),
            LocationType(
                name='outlet',
                allowed_parents=['village']
            ),
        ]
        domain.save()

        # TODO
        # # clear data!
        # for product in Product.by_domain(domain.name):
        #     StockState.objects.filter(
        #         product_id=product._id
        #     ).delete()

        #     transactions = StockTransaction.objects.filter(
        #         product_id=product._id
        #     ).delete()

        #     # TODO delete reports
        #     # StockReport.objects.filter(
        #     # ).delete()

        top_levels = []
        for i in range(num_top_level_locs):
            state = Location(
                site_code='state%d' % (i + 1),
                name='State %d' % (i + 1),
                domain=domain.name,
                location_type='state',
            )
            state.save()
            top_levels.append(state)

        mid_levels = []
        for i in range(num_mid_level_locs):
            village = Location(
                site_code='village%d' % (i + 1),
                name='Village %d' % (i + 1),
                domain=domain.name,
                location_type='village',
                parent=top_levels[randint(0, num_top_level_locs - 1)]
            )
            village.save()
            mid_levels.append(village)

        bottom_levels = []
        for i in range(num_bottom_level_locs):
            loc = Location(
                site_code='outlet%d' % (i + 1),
                name='Outlet %d' % (i + 1),
                domain=domain.name,
                location_type='outlet',
                parent=mid_levels[randint(0, num_mid_level_locs - 1)]
            )
            loc.save()

            SupplyPointCase.create_from_location(domain.name, loc)
            # we have to save again due to weirdness with
            # supply point creation
            loc.save()

            bottom_levels.append(loc)

        # CONFIGURE USER(S)
        users = []
        for i, loc in enumerate(bottom_levels):
            phone_number = randint(100000000, 999999999)

            user = CommCareUser.create(
                domain.name,
                'user-' + str(i) + '-' + domain.name,
                'asdf',
                phone_numbers=phone_number,
                user_data={},
                first_name='main',
                last_name='user'
            )
            user.set_location(loc)
            user.save_verified_number(
                domain.name,
                phone_number,
                verified=True,
                backend_id=domain.default_sms_backend_id
            )
            users.append(user)

        for user in users:
            with freeze_time(datetime.datetime.now() - timedelta(days=num_days)):
                sms.handle(
                    user.get_verified_number(), 'soh pp 50 pq 50 pr 50'
                )

            for day_offset in range(num_days - 1, 0, -1):
                action = 'r' if random.random() < 0.5 else 'l'
                pp = int(random.random() * 10)
                pq = int(random.random() * 10)
                pr = int(random.random() * 10)
                with freeze_time(datetime.datetime.now() - timedelta(days=day_offset)):
                    sms.handle(
                        user.get_verified_number(),
                        '{act} pp {pp} pq {pq} pr {pr}'.format(
                            act=action,
                            pp=pp,
                            pq=pq,
                            pr=pr
                        )
                    )

