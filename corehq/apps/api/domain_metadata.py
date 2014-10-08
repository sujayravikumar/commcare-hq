from django.http import HttpResponse, Http404
from django.views.generic import View
from corehq import Domain

from dimagi.utils.web import json_response


class DomainMetadataAPI(View):
    def get(self, *args, **kwargs):
        domain = Domain.get_by_name(kwargs.get('domain'))
        if not domain:
            raise Http404
        return json_response(self.get_metadata(domain))

    def get_metadata(self, domain):
        return {
            "domain_properties": self.get_domain_properties(domain),
        }

    def get_domain_properties(self, domain):
        return {term: domain[term] for term in domain}
