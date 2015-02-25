import json
import urllib2
from celery.schedules import crontab
from celery.task import periodic_task
from datetime import date
from django.conf import settings
from celery.utils.log import get_task_logger

from corehq.apps.accounting.models import Currency
from corehq.apps.smsbillables.models import SmsBillable

from dimagi.utils.django.email import send_HTML_email


logger = get_task_logger("accounting")


@periodic_task(run_every=crontab(minute=0, hour=0))
def update_exchange_rates(app_id=settings.OPEN_EXCHANGE_RATES_ID):
    try:
        logger.info("Updating exchange rates...")
        rates = json.load(urllib2.urlopen(
            'https://openexchangerates.org/api/latest.json?app_id=%s' % app_id))['rates']
        default_rate = float(rates[Currency.get_default().code])
        for code, rate in rates.items():
            currency, _ = Currency.objects.get_or_create(code=code)
            currency.rate_to_default = float(rate) / default_rate
            currency.save()
            logger.info("Exchange rate for %(code)s updated %(rate)f." % {
                'code': currency.code,
                'rate': currency.rate_to_default,
            })
    except Exception as e:
        logger.error(e.message)

@periodic_task(run_every=crontab(hour=13, minute=0, day_of_month='1'))
def send_billables_missing_gateway_fee(
        date_from=None,
        date_to=None,
        emails=settings.BOOKKEEPER_CONTACT_EMAILS,
):
    date_from = date_from or date.today()
    date_to = date_to or date.today()

    billables_missing_gateway_fee = SmsBillable.objects.filter(
        gateway_fee=None,
        date_sent__gte=date_from,
        date_send__lte=date_to,
    )

    subject = "SMSs with no matching gateway fee - %s" % date.today().strftime("%B %Y")

    for email in emails:
        send_HTML_email(
            subject,
            email,
        )
