from django.utils.translation import ugettext_lazy as _


class TourText(object):
    def __init__(self, title=None, lead=None, prompt=None):
        self.title = title
        self.lead = lead
        self.prompt = prompt


class TourDescription(object):
    NEW_BY_SLUG = {
        'new_app': TourText(
            title=_("Create a New Form"),
            lead=_("Hi there! Thanks for creating an App."),
            prompt=_("The next step is to create a new form. Start a tour "
                     "now to get the most out of the App Builder."),
        )
    }
    RESUME_BY_SLUG = {
        'new_app': TourText(
            title=_("Resume: Create a New Form"),
            lead=_("Hi there! Thanks for creating an App."),
            prompt=_("It looks like you already started a tour of the "
                     "App Builder, but never completed it."
                     "Would you like to resume this tour?"),
        )
    }
    DEFAULT = TourText(
        title=_("Begin Tour"),
        lead=_("This is a tour."),
        prompt=_("Would you like to start this tour?"),
    )

    @classmethod
    def get_by_slug(cls, slug):
        new_text = cls.NEW_BY_SLUG.get(slug, cls.DEFAULT)
        return {
            'new': new_text,
            'resume': cls.RESUME_BY_SLUG.get(slug, new_text),
        }
