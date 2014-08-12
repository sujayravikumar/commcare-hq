from django.http import HttpResponse
from corehq.apps.sms.api import incoming as incoming_sms
from corehq.apps.api.decorators import require_api_key

PERMISSION_SISLOG = "SISLOG"


@require_api_key(permission=PERMISSION_SISLOG)
def sms_in_auth(request, api_key):
    return sms_in(request)


def sms_in(request):
    """
    sender - the number of the person sending the sms
    receiver - the number the sms was sent to
    msgdata - the message
    """
    sender = request.GET.get("sender", None)
    receiver = request.GET.get("receiver", None)
    msgdata = request.GET.get("msgdata", None)
    if sender is None or msgdata is None:
        return HttpResponse(status=400)
    else:
        incoming_sms(sender, msgdata, "SISLOG")
        return HttpResponse()

