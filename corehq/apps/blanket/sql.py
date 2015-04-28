import datetime
from corehq import toggle_enabled
from corehq.apps.blanket.models import SqlQuerySummary
from corehq.toggles import BLANKET
from corehq.util.view_utils import get_request
from dimagi.utils.couch.database import get_db


def get_query_set(manager):
    start_time = datetime.datetime.utcnow()
    query_set = manager._get_query_set()
    end_time = datetime.datetime.utcnow()

    # store metadata
    if toggle_enabled(get_request(), BLANKET):
        query_time = end_time - start_time
        microseconds = 1000000 * query_time.seconds + query_time.microseconds
        print microseconds
        db = get_db(postfix='blanket')
        doc_id = get_request().blanket_request_id
        doc = db.get(doc_id)
        doc.sql_queries.append(
            SqlQuerySummary(
                start_time=start_time,
                end_time=end_time,
            )
        )
        doc.save()

    return query_set
