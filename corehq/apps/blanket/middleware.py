import logging
from datetime import datetime
import couchdbkit
from corehq.apps.blanket import couchwrapper
from corehq.apps.blanket.sql import get_query_set

from dimagi.utils.couch.database import get_db
from corehq.toggles import BLANKET

from .factory import RequestModelFactory, ResponseModelFactory
from .models import *
from .profiler import Profiler

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
        if True:
            # self._apply_dynamic_mappings()

            # Hook in sql profiler
            from django.db.models import Manager
            if not Manager._get_query_set:
                Manager._get_query_set = Manager.get_query_set
                Manager.get_query_set = get_query_set

            # Hook in couch profiler
            self.view_offset = len(getattr(couchdbkit.client.ViewResults, '_queries', []))
            self.get_offset = len(getattr(couchdbkit.client.Database, '_queries', []))

            request.blanket_is_intercepted = True
            request.profiler = Profiler()
            request.profiler.start_python_profiler()
            request_model = RequestModelFactory(request).construct_request_model()
            self.db.save_doc(request_model)
            request.blanket_request_id = request_model['_id']
        #DataCollector().configure(request_model)


    def _process_response(self, response, request):

        request.profiler.stop_python_profiler()

        doc = self.db.get(request.blanket_request_id)
        request_model = BlanketRequestDocument.wrap(doc)
        request_model.line_profile = request.profiler.finalize()
        request_model.end_time = datetime.now()
        request_model.time_taken = self.time_taken(request_model.start_time, request_model.end_time)


        gets = getattr(couchwrapper.DebugDatabase, '_queries', [])
        views = getattr(couchwrapper.DebugViewResults, '_queries', [])

        debug_doc = CouchQuerySummary()
        for ix, r in enumerate(gets[self.get_offset:], start=1):
            debug_doc.doc_requests.append(r)
        for ix, v in enumerate(views[self.view_offset:], start=1):
            debug_doc.view_requests.append(v)

        #summary level info
        debug_doc.total_doc_requests = len(gets[self.get_offset:])
        debug_doc.total_doc_time = sum([x['duration'] for x in gets[self.get_offset:]])

        debug_doc.total_view_requests = len(views[self.view_offset:])
        debug_doc.total_view_time = sum([x['duration'] for x in views[self.view_offset:]])

        print debug_doc

        response_model = ResponseModelFactory(response).construct_response_model()
        self.db.save_doc(response_model)

        request_model.response = response_model
        self.db.save_doc(request_model)


        #collector = DataCollector()
        #collector.stop_python_profiler()
        #silk_request = collector.request
#        if silk_request:
#            silk_response = ResponseModelFactory(response).construct_response_model()
#            silk_response.save()
#            silk_request.end_time = timezone.now()
#            collector.finalise()
#            silk_request.save()
#        else:
#            Logger.error(
#                'No request model was available when processing response. Did something go wrong in '
#                'process_request/process_view?'
#            )
#
    def process_response(self, request, response):
        if getattr(request, 'blanket_is_intercepted', False):
            self._process_response(response, request)
            return response
