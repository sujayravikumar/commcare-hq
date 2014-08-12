from django.http import HttpResponse
from corehq.apps.sms.util import domains_for_phone, users_for_phone
from corehq.apps.unicel import api
from corehq.apps.api.decorators import require_api_key
import json

PERMISSION_UNICEL = "UNICEL"


@require_api_key(permission=PERMISSION_UNICEL)
def incoming_auth(request, api_key):
    return incoming(request)


def incoming(request):
    """
    The inbound endpoint for UNICEL's API.
    """
    # for now just save this information in the message log and return
    message = api.create_from_request(request)
    return HttpResponse(json.dumps({'status': 'success', 'message_id': message._id}), 'text/json')
