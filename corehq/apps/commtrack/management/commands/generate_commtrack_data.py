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
from datetime import timedelta
import datetime
from corehq.apps.commtrack import sms
import random
from corehq.apps.users.models import CommCareUser
from random import randint
from freezegun import freeze_time

NUM_TOP_LEVEL_LOCS = 1
NUM_MID_LEVEL_LOCS = 3
NUM_BOTTOM_LEVEL_LOCS = 10
NUM_DAYS = 5


class Command(BaseCommand):
    args = '<domain>'

    def generate_data(self, domain_name):
        def configure_settings():
            # CONFIGURE SETTINGS
            ct_settings = CommtrackConfig.for_domain(domain.name)
            ct_settings.consumption_config = ConsumptionConfig(
                min_transactions=3,
                min_window=3,
                optimal_window=6,
            )
            ct_settings.use_auto_consumption = True
            ct_settings.save()

        def configure_loc_types():
            domain.location_types = [
                LocationType(
                    name='region',
                    allowed_parents=[''],
                    administrative=True
                ),
                LocationType(
                    name='district',
                    allowed_parents=['region'],
                    administrative=True
                ),
                LocationType(
                    name='facility',
                    allowed_parents=['district']
                ),
            ]
            domain.save()

        def build_locations():
            top_levels = []
            for i in range(NUM_TOP_LEVEL_LOCS):
                state = Location(
                    site_code='region%d' % (i + 1),
                    name='Region %d' % (i + 1),
                    domain=domain.name,
                    location_type='region',
                )
                state.save()
                top_levels.append(state)

            mid_levels = []
            for i in range(NUM_MID_LEVEL_LOCS):
                village = Location(
                    site_code='district%d' % (i + 1),
                    name='District %d' % (i + 1),
                    domain=domain.name,
                    location_type='district',
                    parent=top_levels[randint(0, NUM_TOP_LEVEL_LOCS - 1)]
                )
                village.save()
                mid_levels.append(village)

            bottom_levels = []
            for i in range(NUM_BOTTOM_LEVEL_LOCS):
                loc = Location(
                    site_code='facility%d' % (i + 1),
                    name='Facility %d' % (i + 1),
                    domain=domain.name,
                    location_type='facility',
                    parent=mid_levels[randint(0, NUM_MID_LEVEL_LOCS - 1)]
                )
                loc.save()

                SupplyPointCase.create_from_location(domain.name, loc)
                # we have to save again due to weirdness with
                # supply point creation
                loc.save()

                bottom_levels.append(loc)

            return bottom_levels

        def build_users(locs):
            users = []
            for i, loc in enumerate(locs):
                phone_number = '555' + str(randint(100000000, 999999999))

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

            return users

        def submit_data(users, num_days=None):
            num_days = num_days or NUM_DAYS
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

        def create_domain(domain_name):
            domain = Domain.get_or_create_with_name(
                name=domain_name,
                is_active=True,
                secure_submissions=False
            )

            if not domain.commtrack_enabled:
                domain.commtrack_enabled = True
                domain.locations_enabled = True

            domain.save()
            return domain

        domain = create_domain(domain_name)
        configure_settings()
        configure_loc_types()

        supply_point_locs = build_locations()
        users = build_users(supply_point_locs)

        submit_data(users)

    def handle(self, *args, **options):
        # CONFIGURE DOMAIN
        try:
            self.generate_data(args[0])
        except IndexError:
            print 'Must specify domain name'
            return
