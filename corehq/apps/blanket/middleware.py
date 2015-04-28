import logging
import time
from datetime import datetime
import couchdbkit
from corehq.apps.blanket import couchwrapper
from corehq.apps.blanket.sql import execute_sql

from dimagi.utils.couch.database import get_db
from corehq.toggles import BLANKET

from .factory import RequestModelFactory, ResponseModelFactory
from .models import *
from .profiler import Profiler
from .couchwrapper import DebugViewResults, DebugDatabase

Logger = logging.getLogger('blanket')


class BlanketMiddleware(object):

    def __init__(self, *args, **kwargs):
        self.db = get_db(postfix='blanket')

    def _is_enabled(user=None, domain=None):
        return BLANKET.enabled(user) or BLANKET.enabled(domain)

    def time_taken(self, start_time, end_time):
        d = end_time - start_time
        return d.seconds * 1000 + d.microseconds / 1000

    def process_request(self, request):
        if True and not request.path.startswith('/blanket'):
            # self._apply_dynamic_mappings()

            # Hook in sql profiler
            # TODO this can be moved elsewhere
            from django.db.models.sql.compiler import SQLCompiler
            if not hasattr(SQLCompiler, '_execute_sql'):
                SQLCompiler._execute_sql = SQLCompiler.execute_sql
                SQLCompiler.execute_sql = execute_sql

            # Hook in couch profiler
            request.view_offset = len(getattr(couchdbkit.client.ViewResults, '_queries', []))
            request.get_offset = len(getattr(couchdbkit.client.Database, '_queries', []))
            
            if not hasattr(couchdbkit.client, '_ViewResults'):
                couchdbkit.client._ViewResults = couchdbkit.ViewResults
                couchdbkit.client.ViewResults = DebugViewResults

            if not hasattr(couchdbkit.client, '_Database'):
                couchdbkit.client._Database = couchdbkit.Database
                couchdbkit.client.Database = DebugDatabase

            request.blanket_is_intercepted = True
            request.profiler = Profiler()
            request.profiler.start_python_profiler()
            request.start = time.time()
            try:
                request_model = RequestModelFactory(request).construct_request_model()
                self.db.save_doc(request_model)
                request.blanket_request_id = request_model['_id']
            except Exception, e:
                print 'NOT LOGGED'
                request.blanket_is_intercepted = False

    def _process_response(self, response, request):

        request.profiler.stop_python_profiler()

        doc = self.db.get(request.blanket_request_id)
        request_model = BlanketRequestDocument.wrap(doc)
        request_model.line_profile = request.profiler.finalize()
        request_model.end_time = datetime.utcnow()
        request_model.time_taken = (time.time() - request.start) * 1000


        gets = getattr(couchwrapper.DebugDatabase, '_queries', [])
        views = getattr(couchwrapper.DebugViewResults, '_queries', [])

        debug_doc = CouchQuerySummary()
        for ix, r in enumerate(gets[request.get_offset:], start=1):
            debug_doc.doc_requests.append(r)
        for ix, v in enumerate(views[request.view_offset:], start=1):
            debug_doc.view_requests.append(v)

        #summary level info
        debug_doc.total_doc_requests = len(gets[request.get_offset:])
        debug_doc.total_doc_time = sum([x['duration'] for x in gets[request.get_offset:]])

        debug_doc.total_view_requests = len(views[request.view_offset:])
        debug_doc.total_view_time = sum([x['duration'] for x in views[request.view_offset:]])

        response_model = ResponseModelFactory(response).construct_response_model()
        self.db.save_doc(response_model)

        request_model.response = response_model
        request_model.couchdb_queries = debug_doc
        self.db.save_doc(request_model)


    def process_response(self, request, response):
        if getattr(request, 'blanket_is_intercepted', False):
            self._process_response(response, request)
        return response
