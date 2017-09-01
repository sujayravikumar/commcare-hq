import csv
import datetime
import decimal
from mock import MagicMock
from collections import defaultdict, Counter

from django.core.management.base import BaseCommand

from dimagi.utils.chunked import chunked
from dimagi.utils.decorators.memoized import memoized

from corehq.apps.hqcase.utils import bulk_update_cases
from corehq.form_processor.interfaces.dbaccessors import CaseAccessors
from corehq.motech.repeaters.models import RepeatRecord, RepeatRecordAttempt
from corehq.motech.repeaters.dbaccessors import iter_repeat_records_by_domain, get_repeat_record_count
from corehq.util.couch import IterDB
from corehq.util.log import with_progress_bar

from custom.enikshay.case_utils import CASE_TYPE_VOUCHER
from custom.enikshay.const import (
    VOUCHER_ID,
    AMOUNT_APPROVED,
    DATE_FULFILLED,
    DATE_APPROVED,
    FULFILLED_BY_ID,
    FULFILLED_BY_LOCATION_ID,
    INVESTIGATION_TYPE,
    VOUCHER_TYPE,
)
from custom.enikshay.integrations.bets.repeater_generators import VoucherPayload
from custom.enikshay.integrations.bets.views import VoucherUpdate


class Command(BaseCommand):
    help = """
    import payment confirmations of vouchers paid offline
    """
    voucher_id_header = 'id'
    voucher_update_properties = [
        'status',
        'amount',
        'paymentDate',
        'comments',
        'failureDescription',
        'paymentMode',
        'checkNumber',
        'bankName',
        'eventType',
    ]

    voucher_api_properties = [
        'VoucherID',
        'EventOccurDate',
        'EventID',
        'BeneficiaryUUID',
        'BeneficiaryType',
        'Location',
        'Amount',
        'DTOLocation',
        'InvestigationType',
        'PersonId',
        'AgencyId',
        'EnikshayApprover',
        'EnikshayRole',
        'EnikshayApprovalDate',
    ]

    def add_arguments(self, parser):
        parser.add_argument('domain')
        parser.add_argument('filename')
        parser.add_argument(
            '--commit',
            action='store_true',
            dest='commit',
            default=False,
        )

    def handle(self, domain, filename, **options):
        self.domain = domain
        self.accessor = CaseAccessors(domain)
        self.commit = options['commit']
        self.bad_payloads = 0

        with open(filename) as f:
            reader = csv.reader(f)
            headers = reader.next()
            missing_headers = set(self.voucher_update_properties) - set(headers)
            if missing_headers:
                print "Missing the following headers:"
                for header in missing_headers:
                    print " ", header
                print "\nAborting."
                return

            rows = list(reader)

        print "Received info on {} vouchers.  Headers are:".format(len(rows))
        for header in headers:
            print header

        unrecognized_vouchers = []
        unapproved_vouchers = []
        voucher_ids_to_update = set()
        voucher_updates = []

        case_id_to_confirmation_status = defaultdict(lambda: "not_applicable")

        print "Parsing rows from spreadsheet"
        for row in with_progress_bar(rows):
            voucher_id = row[headers.index(self.voucher_id_header)]
            voucher = self.all_vouchers_in_domain.get(voucher_id)
            if not voucher:
                unrecognized_vouchers.append(row)
            elif self._missing_key_properties(voucher) or not self._is_approved(voucher):
                unapproved_vouchers.append((row, voucher))
                case_id_to_confirmation_status[voucher.case_id] = "unapproved"
            else:
                voucher_ids_to_update.add(voucher_id)
                raw_amount = row[headers.index('amount')]
                update = VoucherUpdate(
                    id=voucher.case_id,
                    amount=decimal.Decimal(raw_amount) if raw_amount else raw_amount,
                    paymentDate=datetime.datetime.now(),
                    **{
                        prop: row[headers.index(prop)]
                        for prop in self.voucher_update_properties
                        if prop not in ('amount', 'paymentDate')
                    }
                )
                update._voucher = voucher
                voucher_updates.append(update)
                case_id_to_confirmation_status[voucher.case_id] = "to_update"

        print "{} total rows, {} unique voucher ids".format(
            len(rows),
            len(set(r[headers.index(self.voucher_id_header)] for r in rows)),
        )
        print "{} unrecognized\n{} unapproved or incomplete\n{} to update".format(
            len(unrecognized_vouchers),
            len(unapproved_vouchers),
            len(voucher_updates),
        )

        self.log_voucher_updates(voucher_updates)
        self.log_unrecognized_vouchers(headers, unrecognized_vouchers)
        self.log_unapproved_vouchers(headers, unapproved_vouchers)
        self.log_unmodified_vouchers(voucher_ids_to_update)
        self.log_all_vouchers_in_domain(case_id_to_confirmation_status)
        self.update_vouchers(voucher_updates)
        self.reconcile_repeat_records(voucher_updates)
        print "Couldn't generate payloads for {} vouchers".format(self.bad_payloads)

    @property
    @memoized
    def all_vouchers_in_domain(self):
        voucher_ids = self.accessor.get_case_ids_in_domain(CASE_TYPE_VOUCHER)
        return {
            voucher.get_case_property(VOUCHER_ID): voucher
            for voucher in self.accessor.iter_cases(voucher_ids)
        }

    @staticmethod
    def _is_approved(voucher):
        return (
            voucher.get_case_property('state') in ('approved', 'paid',)
            or voucher.get_case_property('voucher_approval_status') in ('approved', 'partially_approved')
        )

    @staticmethod
    def _missing_key_properties(voucher):
        return not all(voucher.get_case_property(prop) for prop in [
            DATE_FULFILLED,
            DATE_APPROVED,
            FULFILLED_BY_ID,
            FULFILLED_BY_LOCATION_ID,
        ])

    def write_csv(self, filename, headers, rows):
        filename = "voucher_confirmations-{}.csv".format(filename)
        print "writing {} rows to {}".format(len(rows), filename)
        with open(filename, 'w') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            writer.writerows(rows)

    def _get_api_payload(self, voucher):
        try:
            return VoucherPayload.create_voucher_payload(voucher)
        except Exception:
            self.bad_payloads += 1
            return defaultdict(lambda: "PAYLOAD_ERROR")

    def log_voucher_updates(self, voucher_updates):
        headers = ['ReadableID'] + self.voucher_api_properties + self.voucher_update_properties

        def make_row(voucher_update):
            api_payload = self._get_api_payload(voucher_update._voucher)
            return [voucher_update._voucher.get_case_property(VOUCHER_ID)] + [
                api_payload[prop] for prop in self.voucher_api_properties
            ] + [
                voucher_update[prop] for prop in self.voucher_update_properties
            ]

        print "logging voucher updates"
        rows = map(make_row, with_progress_bar(voucher_updates))
        self.write_csv('updates', headers, rows)

    def log_unrecognized_vouchers(self, headers, unrecognized_vouchers):
        print "logging unrecognized vouchers"
        self.write_csv('unrecognized', headers, unrecognized_vouchers)

    def log_unapproved_vouchers(self, headers, unapproved_vouchers):
        print "logging unapproved vouchers"
        props = [
            'state',
            'voucher_approval_status',
            AMOUNT_APPROVED,
            DATE_FULFILLED,
            DATE_APPROVED,
            FULFILLED_BY_ID,
            FULFILLED_BY_LOCATION_ID,
            INVESTIGATION_TYPE,
            VOUCHER_TYPE,
        ]
        headers = ['voucher_case_id', 'URL'] + props + headers
        rows = [
            [
                voucher.case_id,
                'https://enikshay.in/a/enikshay/reports/case_data/{}'.format(voucher.case_id),
            ] + [
                voucher.get_case_property(prop) for prop in props
            ] + row
            for row, voucher in unapproved_vouchers
        ]
        self.write_csv('unapproved_or_incomplete', headers, rows)

    def log_unmodified_vouchers(self, voucher_ids_to_update):
        unmodified_vouchers = [
            voucher for voucher_id, voucher in self.all_vouchers_in_domain.items()
            if voucher_id not in voucher_ids_to_update and self._is_approved(voucher)
        ]
        headers = ['ReadableID', 'URL', 'state', 'voucher_approval_status'] + self.voucher_api_properties

        def make_row(voucher):
            api_payload = self._get_api_payload(voucher)
            return [
                voucher.get_case_property(VOUCHER_ID),
                'https://enikshay.in/a/enikshay/reports/case_data/{}'.format(voucher.case_id),
                voucher.get_case_property('state'),
                voucher.get_case_property('voucher_approval_status'),
            ] + [
                api_payload[prop] for prop in self.voucher_api_properties
            ]

        print "logging unmodified vouchers"
        rows = map(make_row, with_progress_bar(unmodified_vouchers))
        self.write_csv('unmodified', headers, rows)

    def log_all_vouchers_in_domain(self, case_id_to_confirmation_status):
        voucher_ids = self.accessor.get_case_ids_in_domain(CASE_TYPE_VOUCHER)
        vouchers = list(self.accessor.iter_cases(voucher_ids))
        voucher_id_counts = Counter(v.get_case_property(VOUCHER_ID) for v in vouchers)
        headers = [
            "ReadableID",
            "URL",
            "state",
            "PaymentConfirmationStatus",
            "# Vouchers with ID",
        ]
        rows = [[
            voucher.get_case_property(VOUCHER_ID),
            'https://enikshay.in/a/enikshay/reports/case_data/{}'.format(voucher.case_id),
            voucher.get_case_property('state'),
            case_id_to_confirmation_status[voucher.case_id],
            voucher_id_counts[voucher.get_case_property(VOUCHER_ID)],
        ] for voucher in vouchers]
        self.write_csv('all_vouchers', headers, rows)

    def update_vouchers(self, voucher_updates):
        print "updating voucher cases"
        for chunk in chunked(with_progress_bar(voucher_updates), 100):
            updates = [
                (update.case_id, update.properties, False)
                for update in chunk
            ]
            if self.commit:
                bulk_update_cases(self.domain, updates)

    def reconcile_repeat_records(self, voucher_updates):
        """
        Mark updated records as "succeeded", all others as "cancelled"
        Delete duplicate records if any exist
        """
        print "Reconciling repeat records"
        chemist_voucher_repeater_id = 'be435d3f407bfb1016cc89ebbf8146b1'
        lab_voucher_repeater_id = 'be435d3f407bfb1016cc89ebbfc42a47'

        already_seen = set()
        updates_by_voucher_id = {update.id: update for update in voucher_updates}

        headers = ['record_id', 'voucher_id', 'status']
        rows = []

        get_db = (lambda: IterDB(RepeatRecord.get_db())) if self.commit else MagicMock
        with get_db() as iter_db:
            for repeater_id in [chemist_voucher_repeater_id, lab_voucher_repeater_id]:
                print "repeater {}".format(repeater_id)
                records = iter_repeat_records_by_domain(self.domain, repeater_id=repeater_id)
                record_count = get_repeat_record_count(self.domain, repeater_id=repeater_id)
                for record in with_progress_bar(records, record_count):
                    if record.payload_id in already_seen:
                        status = "deleted"
                        iter_db.delete(record)
                    elif record.payload_id in updates_by_voucher_id:
                        # add successful attempt
                        status = "succeeded"
                        attempt = RepeatRecordAttempt(
                            cancelled=False,
                            datetime=datetime.datetime.utcnow(),
                            failure_reason=None,
                            success_response="Paid offline via import_voucher_confirmations",
                            next_check=None,
                            succeeded=True,
                        )
                        record.add_attempt(attempt)
                        iter_db.save(record)
                    else:
                        # mark record as canceled
                        record.add_attempt(RepeatRecordAttempt(
                            cancelled=True,
                            datetime=datetime.datetime.utcnow(),
                            failure_reason="Cancelled during import_voucher_confirmations",
                            success_response=None,
                            next_check=None,
                            succeeded=False,
                        ))
                        iter_db.save(record)

                    already_seen.add(record.payload_id)
                    rows.append([record._id, record.payload_id, status])

        self.write_csv('repeat_records', headers, rows)
