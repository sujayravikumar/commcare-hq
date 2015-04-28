import datetime
from corehq import toggle_enabled
from corehq.toggles import BLANKET
from corehq.util.view_utils import get_request


def get_query_set(manager):
    start_time = datetime.datetime.utcnow()
    query_set = manager._get_query_set()
    end_time = datetime.datetime.utcnow()

    # store metadata TODO
    if toggle_enabled(get_request(), BLANKET):
        query_time = end_time - start_time
        microseconds = 1000000 * query_time.seconds + query_time.microseconds
        print microseconds

    return query_set
