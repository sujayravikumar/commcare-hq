from decimal import Decimal
import logging
from couchdbkit import ResourceNotFound

from django.core.management.base import LabelCommand

from corehq.apps.accounting.models import Currency
from corehq.apps.sms.backend.http_api import HttpBackend
from corehq.apps.sms.models import INCOMING, OUTGOING
from corehq.apps.smsbillables.models import SmsGatewayFee


logger = logging.getLogger('accounting')


def bootstrap_moz_gateway(orm):
    mzn, _ = (orm['accounting.Currency'] if orm else Currency).objects.get_or_create(code='MZN')

    SmsGatewayFee.create_new(
        'SISLOG',
        INCOMING,
        Decimal('1.4625'),
        country_code='258',
        prefix='82',
        currency=mzn,
    )
    SmsGatewayFee.create_new(
        'SISLOG',
        INCOMING,
        Decimal('1.4625'),
        country_code='258',
        prefix='83',
        currency=mzn,
    )
    SmsGatewayFee.create_new(
        'SISLOG',
        INCOMING,
        Decimal('1.4625'),
        country_code='258',
        prefix='84',
        currency=mzn,
    )
    SmsGatewayFee.create_new(
        'SISLOG',
        INCOMING,
        Decimal('0.702'),
        country_code='258',
        prefix='86',
        currency=mzn,
    )
    SmsGatewayFee.create_new(
        'SISLOG',
        INCOMING,
        Decimal('0.702'),
        country_code='258',
        prefix='87',
        currency=mzn,
    )

    backend_id = '7ddf3301c093b793c6020ebf755adb6f'
    try:
        backend = HttpBackend.get(backend_id)
    except ResourceNotFound:
        # for non-production environments
        backend = HttpBackend()
        backend._id = backend_id
        backend.save()
    SmsGatewayFee.create_new(
        backend.get_api_id(),
        OUTGOING,
        Decimal('0.3627'),
        backend_instance=backend._id,
        country_code='258',
        prefix='82',
        currency=mzn,
    )
    SmsGatewayFee.create_new(
        backend.get_api_id(),
        OUTGOING,
        Decimal('0.3627'),
        backend_instance=backend._id,
        country_code='258',
        prefix='83',
        currency=mzn,
    )
    SmsGatewayFee.create_new(
        backend.get_api_id(),
        OUTGOING,
        Decimal('0.3627'),
        backend_instance=backend._id,
        country_code='258',
        prefix='84',
        currency=mzn,
    )
    SmsGatewayFee.create_new(
        backend.get_api_id(),
        OUTGOING,
        Decimal('1.1232'),
        backend_instance=backend._id,
        country_code='258',
        prefix='86',
        currency=mzn,
    )
    SmsGatewayFee.create_new(
        backend.get_api_id(),
        OUTGOING,
        Decimal('1.1232'),
        backend_instance=backend._id,
        country_code='258',
        prefix='87',
        currency=mzn,
    )


class Command(LabelCommand):
    help = "bootstrap MOZ global SMS backend gateway fees"
    args = ""
    label = ""

    def handle(self, *args, **options):
        bootstrap_moz_gateway(None)
