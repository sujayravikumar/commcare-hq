from couchdbkit.ext.django.schema import *


class DocRequest(DocumentSchema):
    view_path = StringProperty()
    doc_id = StringProperty()
    duration = DecimalProperty()
    doc_type = StringProperty()
    response = IntegerProperty()
    stack_trace = ListProperty(required=False)


class ViewRequest(DocumentSchema):
    view_path = StringProperty()
    duration = DecimalProperty()
    offset = IntegerProperty()
    rows = IntegerProperty()
    total_rows = IntegerProperty()
    result_cached = BooleanProperty()
    include_docs = BooleanProperty()


class CouchQuerySummary(DocumentSchema):
    """
    Class to record timings of couch requests
    Will track all of the view requests as well as doc requests with timing and cache information
    """
    duration = DecimalProperty()
    doc_requests = SchemaListProperty(DocRequest)
    total_doc_requests = IntegerProperty()
    total_doc_time = DecimalProperty()

    view_requests = SchemaListProperty(ViewRequest)
    total_view_requests = IntegerProperty()
    total_view_time = DecimalProperty()


class SqlQuerySummary(DocumentSchema):
    start_time = DateTimeProperty()
    end_end = DateTimeProperty()


class BlanketResponseDocument(Document):
    status_code = IntegerProperty()
    raw_body = StringProperty()
    body = StringProperty()
    encoded_headers = StringProperty()


class BlanketRequestDocument(Document):
    path = StringProperty()
    query_params = StringProperty()
    raw_body = StringProperty()
    body = StringProperty()
    method = StringProperty()
    start_time = DateTimeProperty()
    view_name = StringProperty()
    end_time = DateTimeProperty()
    time_taken = FloatProperty()  # In milliseconds
    encoded_headers = StringProperty()
    pyprofile = StringProperty()
    response = SchemaProperty(BlanketResponseDocument)
    line_profile = StringProperty()

    couchdb_queries = SchemaProperty(CouchQuerySummary)
    sql_queries = SchemaListProperty(SqlQuerySummary)
