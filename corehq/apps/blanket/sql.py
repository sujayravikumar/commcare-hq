import datetime
import time
from corehq import toggle_enabled
from corehq.apps.blanket.models import SqlQuerySummary
from corehq.toggles import BLANKET
from corehq.util.view_utils import get_request
from dimagi.utils.couch.database import get_db

from .models import *

def get_query_set(manager):
    start_time = time.time()
    query_set = manager._get_query_set()
    end_time = time.time()

    # store metadata
    if get_request().blanket_is_intercepted:
        query_time = end_time - start_time
        ms = (end_time - start_time) * 1000
        db = get_db(postfix='blanket')
        doc_id = get_request().blanket_request_id
        doc = db.get(doc_id)
        wrapped = BlanketRequestDocument.wrap(doc)
        wrapped.sql_queries.append(
            SqlQuerySummary(
                start_time=start_time,
                end_time=end_time,
            )
        )
        wrapped.save()

    return query_set
