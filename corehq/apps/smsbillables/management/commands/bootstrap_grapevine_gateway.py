from decimal import Decimal
import logging
from django.core.management.base import LabelCommand
from corehq.apps.accounting.models import Currency

from corehq.apps.grapevine.api import GrapevineBackend
from corehq.apps.sms.models import INCOMING, OUTGOING
from corehq.apps.smsbillables.models import SmsGatewayFee, SmsGatewayFeeCriteria
from corehq.apps.smsbillables.utils import get_global_backends_by_class

logger = logging.getLogger('accounting')


def bootstrap_grapevine_gateway(orm):
    # if orm is not None:
    #     fee_class =
    #     SmsGatewayFeeCriteria = orm['smsbillables.SmsGatewayFeeCriteria']
    #     print SmsGatewayFeeCriteria

    relevant_backends = get_global_backends_by_class(GrapevineBackend)
    currency = orm['accounting.Currency'].objects.get_or_create(code="ZAR")[0]

    # any incoming message
    SmsGatewayFee.create_new(
        GrapevineBackend.get_api_id(), INCOMING, Decimal('0.10'),
        currency=currency,
        fee_class=SmsGatewayFee if orm is None else orm['smsbillables.SmsGatewayFee'],
        criteria_class=SmsGatewayFeeCriteria if orm is None else orm['smsbillables.SmsGatewayFeeCriteria'],
    )
    logger.info("Updated Global Grapevine gateway fees.")

    # messages relevant to our Grapevine Backends
    for backend in relevant_backends:
        SmsGatewayFee.create_new(
            GrapevineBackend.get_api_id(), INCOMING, Decimal('0.10'),
            currency=currency, backend_instance=backend.get_id,
            fee_class=SmsGatewayFee if orm is None else orm['smsbillables.SmsGatewayFee'],
            criteria_class=SmsGatewayFeeCriteria if orm is None else orm['smsbillables.SmsGatewayFeeCriteria'],
        )
        SmsGatewayFee.create_new(
            GrapevineBackend.get_api_id(), OUTGOING, Decimal('0.22'),
            currency=currency, backend_instance=backend.get_id,
            fee_class=SmsGatewayFee if orm is None else orm['smsbillables.SmsGatewayFee'],
            criteria_class=SmsGatewayFeeCriteria if orm is None else orm['smsbillables.SmsGatewayFeeCriteria'],
        )

        logger.info("Updated Grapevine fees for backend %s" % backend.name)

class Command(LabelCommand):
    help = "bootstrap Grapevine gateway fees"
    args = ""
    label = ""

    def handle(self, *args, **options):
        bootstrap_grapevine_gateway(None)
