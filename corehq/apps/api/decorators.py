from corehq.apps.api.models import ApiUser
from django.http import HttpResponse

def require_api_key(permission=None):
    def _outer2(fn):
        def _outer(*args, **kwargs):
            api_key = kwargs.get("api_key", "")
            if ApiUser.auth(api_key, api_key, permission):
                response = fn(*args, **kwargs)
            else:
                response = HttpResponse()
                response.status_code = 401
            return response
        return _outer
    return _outer2

