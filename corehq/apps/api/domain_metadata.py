from django.http import HttpResponse, Http404
from django.utils.decorators import method_decorator
from django.views.generic import View
from corehq import Domain
from corehq.apps.domain.decorators import require_superuser
from corehq.apps.es.domains import DomainES

from dimagi.utils.web import json_response


class DomainMetadataAPI(View):
    @method_decorator(require_superuser)
    def get(self, *args, **kwargs):
        domain = Domain.get_by_name(kwargs.get('domain'))
        if not domain:
            raise Http404
        return json_response(self.get_metadata(domain))

    def get_metadata(self, domain):
        return {
            "calculated_properties": self.get_calculated_properties(domain),
            "domain_properties": self.get_domain_properties(domain),
        }

    def get_calculated_properties(self, domain):
        es_data = (DomainES()
                   .in_domains([domain.name])
                   .run()
                   .raw_hits[0]['_source'])
        return {
            raw_hit: es_data[raw_hit]
            for raw_hit in es_data if raw_hit[:3] == 'cp_'
        }

    def get_domain_properties(self, domain):
        return {term: domain[term] for term in domain}
