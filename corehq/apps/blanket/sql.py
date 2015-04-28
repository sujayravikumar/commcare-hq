import time
from django.db.models.sql import MULTI
from corehq.util.view_utils import get_request

from .models import *


def execute_sql(query, result_type=MULTI):
    start_time = time.time()
    result = query._execute_sql(result_type=result_type)
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

    return result
