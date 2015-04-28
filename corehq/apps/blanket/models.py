from couchdbkit.ext.django.schema import *

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
    time_taken = FloatProperty()
    encoded_headers = StringProperty()
    pyprofile = StringProperty()
    response = SchemaProperty(BlanketResponseDocument)

    couchdb_queries = SchemaProperty() # TODO tyler don't screw it up
    sql_queries = SchemaProperty() # TODO nick don't screw it up
