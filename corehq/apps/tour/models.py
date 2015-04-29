from django.core.urlresolvers import reverse
from django.db import models
from corehq.apps.tour.descriptions import TourDescription


class TourArea(object):
    APP_MANAGER = 'app_manager'
    CHOICES = (
        (APP_MANAGER, APP_MANAGER),
    )


class GuidedTour(models.Model):
    """An object that stores information that helps us keep track of and
    trigger guided tours of HQ.
    """
    slug = models.CharField(max_length=25, db_index=True, unique=True)
    area = models.CharField(
        max_length=25,
        db_index=True,
        choices=TourArea.CHOICES
    )
    start_url_name = models.CharField(max_length=25, blank=True)
    start_url_args = models.CharField(max_length=100, blank=True)
    start_url_kwargs = models.CharField(max_length=100, blank=True)
    auto_add_to_new_users = models.BooleanField(default=True, db_index=True)
    description = models.TextField(blank=True)


class QueuedTour(models.Model):
    """This allows us to map a specific tour to a WebUser and Domain so that
    we can bring up queued tours as necessary
    """
    web_user = models.CharField(max_length=80, db_index=True)
    domain = models.CharField(
        max_length=256, null=True, blank=True, db_index=True
    )
    tour = models.ForeignKey(GuidedTour, on_delete=models.PROTECT)
    is_active = models.BooleanField(default=True, db_index=True)
    furthest_step = models.IntegerField(default=0)  # zero indexed, fyi
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    date_completed = models.DateTimeField(null=True, blank=True)

    @property
    def context(self):
        return {
            'slug': self.tour.slug,
            'area': self.tour.area,
            'domain': self.domain,
            'furthest_step': self.furthest_step,
            'text': TourDescription.get_by_slug(self.tour.slug),
            'update_url': reverse('tour_update'),
        }

    @classmethod
    def get_queue_for_user(cls, web_user, area=None, domain=None,
                           as_context=False):
        queue = cls.objects.filter(is_active=True).filter(
            models.Q(web_user=web_user, domain=domain) |
            models.Q(web_user=web_user, domain=None)
        )
        if area is not None:
            queue = queue.filter(tour__area=area)
        if as_context:
            return [q.context for q in queue]
        return queue
