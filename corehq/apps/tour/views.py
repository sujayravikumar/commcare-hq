import json
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.generic import View
from corehq.apps.domain.decorators import login_required
from corehq.apps.tour.models import QueuedTour
from django.utils.translation import ugettext as _


class TourProgressUpdateView(View):
    """This updates the furthest step completed on a given tour. Done by
    posting to this view asynchronously after a tour action.
    """
    urlname = 'tour_update'
    http_method_names = ['post']

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(TourProgressUpdateView, self).dispatch(request, *args, **kwargs)

    @property
    def slug(self):
        return self.request.POST.get('slug')

    @property
    def web_user(self):
        return self.request.user.username

    @property
    def domain(self):
        return self.request.POST.get('domain', None)

    @property
    def step_completed(self):
        return self.request.POST.get('step', 0)

    @property
    def is_complete(self):
        return self.request.POST.get('is_complte', False)

    def post(self, request, *args, **kwargs):
        # Try getting QueuedTour
        try:
            queued_tour = QueuedTour.objects.get(
                web_user=self.web_user,
                domain=self.domain,
                tour__slug=self.slug,
            )
            print "found", queued_tour
            # queued_tour.furthest_step = self.step_completed
            # queued_tour.save()
            # response = {
            #     'success': True,
            #     'updated_context': queued_tour.context,
            # }
            response = {}
        except QueuedTour.DoesNotExist:
            response = {
                'success': False,
                'error': _("Could not fetch queued tour."),
            }
        return HttpResponse(json.dumps(response), type="application/json")
