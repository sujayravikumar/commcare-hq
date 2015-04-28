from optparse import make_option
from django.core.management.base import BaseCommand
from corehq import Domain
from corehq.apps.tour.models import *
from corehq.apps.users.models import WebUser


class Command(BaseCommand):
    help = "An command line tool for managing and viewing guided tours in HQ."
    option_list = BaseCommand.option_list + (
        make_option('--create', action='store_true',  default=False,
                    help='Create a new Guided Tour.'),
        make_option('--list', action='store_true',  default=False,
                    help='List existing Guided Tours'),
        make_option('--queue', action='store_true',  default=False,
                    help='Queue a guided tour for a user.'),
        make_option('--list_queued', action='store_true',  default=False,
                    help='List the queue of tours for a user.'),
    )

    def handle(self, *args, **options):
        if options.get('create', False):
            self.stdout.write("Let's create a guided tour.")
            self.prompt_create()
            return
        if options.get('list', False):
            self.stdout.write("Fetching list of tours...")
            self.list_tours()
            return
        if options.get('queue', False):
            self.stdout.write("Let's queue a tour for a web user.")
            self.queue_tour()
            return
        if options.get('list_queued', False):
            self.stdout.write("Who would you like to see the active tour "
                              "queue for?")
            self.queue_list()
            return

    def prompt_create(self):
        tour_area = self._get_tour_area()
        if self._create_tour(tour_area):
            self.stdout.write("Action complete.")
        else:
            self.stdout.write("Tour was not created or updated.")

    def list_tours(self):
        self.stdout.write("--------------\nExisting "
                          "tours <slug> [<area>]\n--------------")
        if GuidedTour.objects.all().count() < 1:
            self.stdout.write("It looks like you haven't created any tours. "
                              "Use option --create")
        for tour in GuidedTour.objects.all():
            self.stdout.write("%s [%s]" % (tour.slug, tour.area))
        self.stdout.write("...that's all, folks")

    def queue_tour(self):
        web_user = self._get_web_user()
        domain = self._get_domain()
        tour = self._get_tour_by_slug()
        self.stdout.write("Creating tour queue for %(web_user)s%(domain)s "
                          "for the tour %(tour_slug)s" % {
                          'web_user': web_user,
                          'domain': (' (%s)' % domain) if domain else "",
                          'tour_slug': tour.slug,
                          })
        queued_tour = QueuedTour.objects.create(
            web_user=web_user,
            domain=domain,
            tour=tour,
        )
        queued_tour.save()
        self.stdout.write("Tour queued.")

    def queue_list(self):
        web_user = self._get_web_user()
        active_tours = QueuedTour.objects.filter(web_user=web_user,
                                                 is_active=True).all()
        self.stdout.write("--------------\nExisting "
                          "tours <slug> [<area>]\n--------------")
        if active_tours.count() < 1:
            self.stdout.write("No active tours queued for user. "
                              "Use option --queue")
        for tour_queue in active_tours:
            self.stdout.write("%(tour_slug)s [%(tour_area)s]\nDesc: %(desc)s"
                              "\n\n" % {
                              'tour_slug': tour_queue.tour.slug,
                              'tour_area': tour_queue.tour.area,
                              'desc': tour_queue.tour.description,
                              })
        self.stdout.write("...that's all, folks")

    def _get_tour_area(self):
        available_areas = dict(TourArea.CHOICES).keys()
        tour_area = raw_input(
            "What area is the tour going to be in? Available areas are: "
            "%s\n" % '\n- '.join(available_areas)
        )
        if tour_area not in available_areas:
            self.stdout.write("Not a valid area, let's try this again.")
            return self._get_tour_area()
        return tour_area

    def _create_tour(self, tour_area):
        """Creates a new tour
        """
        tour_slug = raw_input(
            "Tour slug: "
        )
        tour, is_new = GuidedTour.objects.get_or_create(
            slug=tour_slug, area=tour_area,
        )
        if not is_new:
            self.stdout.write("That tour already exists.")
            confirm_update = raw_input(
                "Type 'update' to update tour.\n"
            )
            if confirm_update == 'update':
                return self._update_tour(tour)
            return False
        return self._update_tour(tour)

    def _update_tour(self, tour_obj):
        """Updates all relevant / optional fields in a tour.
        Returns True when the tour is updated.
        """
        tour_obj.description = self._skip_or_update(
            'Description', tour_obj.description
        )
        auto_add = raw_input(
            "Auto Add to New users? [y/n]\n (Current setting: %s)\n"
            % ("y" if tour_obj.auto_add_to_new_users else "n")
        )
        if auto_add == 'y':
            tour_obj.auto_add_to_new_users = True
        elif auto_add == 'n':
            tour_obj.auto_add_to_new_users = False

        tour_obj.start_url_name = self._skip_or_update(
            'Start urlname', tour_obj.description
        )
        tour_obj.start_url_args = self._skip_or_update(
            'Start URL kwargs as CSV list', tour_obj.start_url_kwargs
        )
        tour_obj.start_url_kwargs = self._skip_or_update(
            "Start URL kwargs as (<key>,<val>) CSV list",
            tour_obj.start_url_kwargs
        )
        tour_obj.save()
        return True

    def _skip_or_update(self, desc, current_val):
        new_val = raw_input(
            "\n - %(desc)s:\n%(current_val)s\nType in the new value below or "
            "type 'skip' to skip update.\n" % {
                'desc': desc if desc else "<NO VALUE>",
                'current_val': current_val,
            }
        )
        if new_val != 'skip':
            return new_val
        return current_val

    def _get_web_user(self):
        """Returns an existing web user's username (string). Checks to see
        if the username specified actually matches an existing Web User on HQ.
        If it doesn't recursively prompt until a real Web User is found
        :return: (string) WebUser's username
        """
        username = raw_input(
            "Web User (username): "
        )
        web_user = WebUser.get_by_username(username=username)
        if web_user is None:
            self.stdout.write("Couldn't find that user. Let's try this again.")
            return self._get_web_user()
        return username

    def _get_domain(self):
        """Returns a domain name (string) of a prompted domain name. Verifies
        that the domain actually exists. If it doesn't, recursively prompt the
        user until a real domain is found.
        :return: (string) domain name
        """
        domain_name = raw_input(
            "Domain (can leave blank to apply to all): "
        )
        if not domain_name:
            self.stdout.write("Applying to ALL domains.")
            return None
        domain = Domain.get_by_name(domain_name)
        if domain is None:
            self.stdout.write("Couldn't find that domain. "
                              "Let's try this again.")
            return self._get_domain()
        return domain_name

    def _get_tour_by_slug(self):
        """Returns a GuidedTour object found by a given slug. Will recursively
        attempt to fetch a GuidedTour if no tour is found for a given slug.
        :return: GuidedTour object
        """
        tour_slug = raw_input(
            "Tour Slug: "
        )
        try:
            tour = GuidedTour.objects.get(slug=tour_slug)
            return tour
        except GuidedTour.DoesNotExist:
            self.stdout.write("That tour does not exist. Let's try this again.")
            return self._get_tour_by_slug()

