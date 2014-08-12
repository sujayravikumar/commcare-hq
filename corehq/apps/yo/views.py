from django.http import HttpResponse
from corehq.apps.sms.api import incoming as incoming_sms
from corehq.apps.api.decorators import require_api_key

PERMISSION_YO = "YO"


@require_api_key(permission=PERMISSION_YO)
def sms_in_auth(request, api_key):
    return sms_in(request)


def sms_in(request):
    dest = request.GET.get("dest")
    sender = request.GET.get("sender")
    message = request.GET.get("message")
    incoming_sms(sender, message, "YO")
    return HttpResponse("OK")

