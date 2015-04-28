import logging

from dimagi.utils.couch.database import get_db
from corehq.toggles import BLANKET

from .factory import RequestModelFactory, ResponseModelFactory
from .models import *

Logger = logging.getLogger('blanket')


class BlanketMiddleware(object):

    def __init__(self, *args, **kwargs):
        self.db = get_db(postfix='blanket')

    def _is_enabled(user=None, domain=None):
        return BLANKET.enabled(user) or BLANKET.enabled(domain)

    def process_request(self, request):
        if True:
            # self._apply_dynamic_mappings()

            # Hook in sql profiler
#            if not hasattr(SQLCompiler, '_execute_sql'):
#                SQLCompiler._execute_sql = SQLCompiler.execute_sql
#                SQLCompiler.execute_sql = execute_sql
#
            # Hook in couch profiler
            request.blanket_is_intercepted = True
            request_model = RequestModelFactory(request).construct_request_model()
            self.db.save_doc(request_model)
            request.blanket_request_id = request_model['_id']
        #DataCollector().configure(request_model)


    def _process_response(self, response, request):

        doc = self.db.get(request.blanket_request_id)
        request_model = BlanketRequestDocument.wrap(doc)

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
