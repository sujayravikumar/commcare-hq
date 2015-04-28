import datetime


def get_query_set(manager):
    start_time = datetime.datetime.utcnow()
    query_set = manager._get_query_set()
    end_time = datetime.datetime.utcnow()

    # store metadata
    query_time = end_time - start_time
    microseconds = 1000000 * query_time.seconds + query_time.microseconds
    print microseconds

    return query_set
