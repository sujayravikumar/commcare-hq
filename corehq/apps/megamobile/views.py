from corehq.apps.sms.api import incoming as incoming_sms
from corehq.apps.megamobile.api import MegamobileBackend
from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from corehq.apps.api.decorators import require_api_key

PERMISSION_MEGAMOBILE = "MEGAMOBILE"


@csrf_exempt
@require_api_key(permission=PERMISSION_MEGAMOBILE)
def sms_in_auth(request, api_key):
    return sms_in(request)


@csrf_exempt
def sms_in(request):
    pid = request.GET.get("pid", None)
    msg = request.GET.get("msg", None)
    cel = request.GET.get("cel", None)
    tcs = request.GET.get("tcs", None)

    megamobile_attrs = {
        "megamobile_pid" : pid,
        "megamobile_tcs" : tcs,
    }

    phone_number = "%s%s" % ("63", cel)
    incoming_sms(
        phone_number,
        msg,
        MegamobileBackend.get_api_id(),
        backend_attributes=megamobile_attrs
    )
    return HttpResponse("")

