from collections import defaultdict, namedtuple
from optparse import make_option
from django.core.management.base import BaseCommand
from casexml.apps.case.cleanup import rebuild_case
from casexml.apps.case.models import CommCareCase
from corehq.elastic import stream_es_query, ES_URLS, ADD_TO_ES_FILTER
import dateutil.parser as dparser
import csv
import logging
from dimagi.utils.chunked import chunked

logger = logging.getLogger(__name__)

FormCaseData = namedtuple('FormCaseData',
                          'form_id received_on case_id action_exists domain')


def forms_with_cases(domain=None, since=None, chunksize=500):
    q = {
        "filter": {
            "and": [
                {
                    "bool": {
                        "must_not": {
                            "missing": {
                                "field": "__retrieved_case_ids",
                                "existence": True,
                                "null_value": True
                            }
                        }
                    }
                }
            ]
        },
        "sort": [{"domain.exact": {"order": "asc"}}]
    }
    params = {"domain.exact": domain} if domain else {}
    if since:
        q["filter"]["and"][0]["bool"]["must"] = {
            "range": {
                "received_on": {"from": since.strftime("%Y-%m-%d")}
            }
        }
    q["filter"]["and"].extend(ADD_TO_ES_FILTER["forms"][:])
    return stream_es_query(
        params=params,
        q=q,
        es_url=ES_URLS["forms"],
        fields=["__retrieved_case_ids", "domain", "received_on"],
        chunksize=chunksize,
    )


def case_ids_by_xform_id(xform_ids):
    result = defaultdict(list)
    for row in CommCareCase.get_db().view('case/by_xform_id', keys=xform_ids,
                                          reduce=False):
        result[row["key"]].append(row["id"])
    return dict(result)


def iter_forms_with_cases(domain, since, chunksize=500):
    for form_list in chunked(forms_with_cases(domain, since), chunksize):
        case_id_mapping = case_ids_by_xform_id([f["_id"] for f in form_list])
        for form in form_list:
            form_id = form["_id"]
            f_case_ids = form["fields"]["__retrieved_case_ids"]
            f_domain = form["fields"]["domain"]
            received_on = form["fields"]["received_on"]
            for case_id in f_case_ids:
                yield FormCaseData(
                    form_id=form_id,
                    received_on=received_on,
                    case_id=case_id,
                    action_exists=case_id in case_id_mapping.get(form_id, []),
                    domain=f_domain
                )


def handle_problematic_data(form_case_datas, csv_writer, verbose=False,
                            rebuild=False):
    case_data = CommCareCase.get_db().view(
        '_all_docs',
        keys=[d.case_id for d in form_case_datas]
    )
    cases = set([c["id"] for c in case_data if 'id' in c])
    for d in form_case_datas:
        error = "action_missing" if d.case_id in cases else "nonexistent_case"
        csv_writer.writerow([d.domain, d.case_id, d.form_id, d.received_on,
                             error])
        if verbose and error == "nonexistent_case":
            logger.info("Case (%s) from form (%s) does not exist" % (
                d.case_id, d.form_id))
        elif verbose and error == "action_missing":
            logger.info("Case (%s) missing action for form (%s)" % (
                d.case_id, d.form_id))
        if rebuild:
            if verbose:
                logger.info("rebuilding case (%s) from scratch" % d.case_id)
            try:
                rebuild_case(d.case_id)
            except Exception as e:
                logger.info("Case Rebuild Failure: %s" % e)


class Command(BaseCommand):
    args = '<domain>'
    help = ('Checks all forms in a domain '
            'to make sure their cases were properly updated.')

    option_list = BaseCommand.option_list + (
        make_option('-s', '--since',
                    help="Begin check at this date."),
        make_option('-f', '--filename',
                    help="Save output to this file."),
        make_option('-r', '--rebuild', action="store_true",
                    help="Rebuild cases that were found to be corrupt"),
        make_option('-c', '--chunk',
                    help="Set the chunk size"),
        make_option('--verbose', action="store_true",
                    help="Verbose"),
    )

    def handle(self, *args, **options):
        domain = args[0] if len(args) == 1 else None
        since = (dparser.parse(options["since"], fuzzy=True)
                 if options.get("since") else None)
        filename = (options.get("filename")
                    or ("case_integrity" + ("_%s" % domain if domain else "")))
        chunksize = options.get("chunk") or 500
        if not filename.endswith(".csv"):
            filename = "%s.csv" % filename
        rebuild = options.get("rebuild")
        verbose = options.get("verbose")
        logger.info("writing to file: %s" % filename)

        with open(filename, 'wb+') as csvfile:
            csv_writer = csv.writer(csvfile, delimiter=',',
                                    quotechar='|', quoting=csv.QUOTE_MINIMAL)
            csv_writer.writerow(
                ['Domain', 'Case ID', 'Form ID', 'Form Recieved On', 'Error'])

            problematic = []
            for d in iter_forms_with_cases(domain, since, chunksize):
                if not d.action_exists:
                    problematic.append(d)

                if len(problematic) > chunksize:
                    handle_problematic_data(problematic, csv_writer,
                                            verbose=verbose, rebuild=rebuild)
                    problematic = []
            handle_problematic_data(problematic, csv_writer,
                                    verbose=verbose, rebuild=rebuild)
