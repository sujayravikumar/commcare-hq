from django.core.urlresolvers import reverse

from corehq.apps.hqwebapp.views import BasePageView
from dimagi.utils.decorators.memoized import memoized
from dimagi.utils.couch.database import get_db


class BlanketView(BasePageView):
    page_title = 'Blanket - stay warm'
    page_name = 'Blanket'

    @property
    @memoized
    def db(self):
        return get_db(postfix='blanket')

class BlanketListView(BlanketView):

    urlname = 'blanket_list'
    template_name = 'blanket/index.html'

    @property
    @memoized
    def blankets(self):
        return self.db.all_docs(limit=10, include_docs=True).all()

    @property
    def page_context(self):
        return {
            'blankets': self.blankets
        }

    @property
    def page_url(self):
        return reverse(self.urlname)


class BlanketShowView(BlanketView):

    urlname = 'blanket_show'
    template_name = 'blanket/show.html'

    @property
    @memoized
    def blanket(self):
        return self.db.get(self.blanket_id)

    @property
    @memoized
    def blanket_id(self):
        return self.kwargs.get('blanket_id', None)

    @property
    @memoized
    def blanket(self):
        return self.db.get(self.blanket_id)

    @property
    def page_context(self):
        return {
            'blanket': self.blanket
        }

    @property
    def page_url(self):
        return reverse(self.urlname, args=[self.blanket_id])

