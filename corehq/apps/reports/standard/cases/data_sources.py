import copy
import logging
from couchdbkit import ResourceNotFound, RequestFailed
import dateutil
from django.core import cache
from django.core.urlresolvers import reverse, NoReverseMatch
from django.template.defaultfilters import yesno
from django.utils import html
from django.utils.translation import ugettext as _, ugettext
import simplejson
from casexml.apps.case.models import CommCareCaseAction
from corehq.apps.api.es import ReportCaseES
from corehq.apps.groups.models import Group
from corehq.apps.reports.api import ReportDataSource
from corehq.apps.reports.filters.search import SearchFilter
from corehq.apps.users.models import CommCareUser, CouchUser
from corehq.pillows.base import restore_property_dict
from dimagi.utils.couch.database import get_db
from dimagi.utils.decorators.memoized import memoized


class CaseInfo(object):
    def __init__(self, report, case):
        """
        case is a dict object of the case doc
        """
        self.case = case
        self.report = report

    @property
    def case_type(self):
        return self.case['type']

    @property
    def case_name(self):
        return self.case['name']

    @property
    def case_id(self):
        return self.case['_id']

    @property
    def external_id(self):
        return self.case['external_id']

    @property
    def case_detail_url(self):
        try:
            return reverse('case_details', args=[self.report.domain, self.case_id])
        except NoReverseMatch:
            return None

    @property
    def is_closed(self):
        return self.case['closed']

    def _dateprop(self, prop, iso=True):
        val = self.report.date_to_json(self.parse_date(self.case[prop]))
        if iso:
            val = 'T'.join(val.split(' ')) if val else None
        return val

    @property
    def opened_on(self):
        return self._dateprop('opened_on')

    @property
    def modified_on(self):
        return self._dateprop('modified_on')

    @property
    def closed_on(self):
        return self._dateprop('closed_on')

    @property
    def creating_user(self):
        creator_id = None
        for action in self.case['actions']:
            if action['action_type'] == 'create':
                action_doc = CommCareCaseAction.wrap(action)
                creator_id = action_doc.get_user_id()
                break
        if not creator_id:
            return None
        return self._user_meta(creator_id)

    def _user_meta(self, user_id):
        return {'id': user_id, 'name': self._get_username(user_id)}

    @property
    def owner(self):
        if self.owning_group and self.owning_group.name:
            return ('group', {'id': self.owning_group._id, 'name': self.owning_group.name})
        else:
            return ('user', self._user_meta(self.user_id))

    @property
    def owner_type(self):
        return self.owner[0]

    @property
    def user_id(self):
        return self.report.individual or self.owner_id

    @property
    def owner_id(self):
        if 'owner_id' in self.case:
            return self.case['owner_id']
        elif 'user_id' in self.case:
            return self.case['user_id']
        else:
            return ''

    @property
    @memoized
    def owning_group(self):
        mc = cache.get_cache('default')
        cache_key = "%s.%s" % (Group.__class__.__name__, self.owner_id)
        try:
            if mc.has_key(cache_key):
                cached_obj = simplejson.loads(mc.get(cache_key))
                wrapped = Group.wrap(cached_obj)
                return wrapped
            else:
                group_obj = Group.get(self.owner_id)
                mc.set(cache_key, simplejson.dumps(group_obj.to_json()))
                return group_obj
        except Exception:
            return None

    @property
    @memoized
    def owner_doc(self, wrap=False):
        doc = None
        if self.owner_id:
            try:
                doc = get_db().get(self.owner_id)
            except ResourceNotFound:
                pass
        if not doc:
            return None

        if wrap:
            class_ = {
                'CommCareUser': CommCareUser,
                'Group': Group,
            }.get(doc['doc_type'])
            return class_.wrap(doc)
        else:
            return doc

    @memoized
    def _get_username(self, user_id):
        username = self.report.usernames.get(user_id)
        if not username:
            mc = cache.get_cache('default')
            cache_key = "%s.%s" % (CouchUser.__class__.__name__, user_id)

            try:
                if mc.has_key(cache_key):
                    user_dict = simplejson.loads(mc.get(cache_key))
                else:
                    user_obj = CouchUser.get_by_user_id(user_id) if user_id else None
                    if user_obj:
                        user_dict = user_obj.to_json()
                    else:
                        user_dict = {}
                    cache_payload = simplejson.dumps(user_dict)
                    mc.set(cache_key, cache_payload)
                if user_dict == {}:
                    return None
                else:
                    user_obj = CouchUser.wrap(user_dict)
                    username = user_obj.username
            except Exception:
                return None
        return username

    def parse_date(self, date_string):
        try:
            date_obj = dateutil.parser.parse(date_string)
            return date_obj
        except:
            return date_string


class CaseDisplay(CaseInfo):
    @property
    def closed_display(self):
        return yesno(self.is_closed, "closed,open")

    @property
    def case_link(self):
        url = self.case_detail_url
        if url:
            return html.mark_safe("<a class='ajax_dialog' href='%s' target='_blank'>%s</a>" % (
                self.case_detail_url, html.escape(self.case_name)))
        else:
            return "%s (bad ID format)" % self.case_name

    @property
    def opened_on(self):
        return self._dateprop('opened_on', False)

    @property
    def modified_on(self):
        return self._dateprop('modified_on', False)

    @property
    def owner_display(self):
        owner_type, owner = self.owner
        if owner_type == 'group':
            return '<span class="label label-inverse">%s</span>' % owner['name']
        else:
            return owner['name']

    def user_not_found_display(self, user_id):
        return _("Unknown [%s]") % user_id

    @property
    def creating_user(self):
        user = super(CaseDisplay, self).creating_user
        if user is None:
            return _("No data")
        else:
            return user['name'] or self.user_not_found_display(user['id'])


class ReportCaseDataSource(ReportDataSource):
    slug = 'reportcase_datasource'

    def __init__(self, config=None):
        super(ReportCaseDataSource, self).__init__(config=config)
        self.domain = self.config.get('domain', None)
        self.es = ReportCaseES(self.domain)

    def default_slugs(self):
        return [
            #'case_id',
            'type',
            'name',
            #'detail_url',
            'closed',
            'opened_on',
            'modified_on',
            'closed_on',
            'opened_by',
            'owner_id',
            'external_id',
        ]

    def slugs(self):
        """
        Return the various properties of the reportcase?
        :return:
        """
        return self.config.get('case_properties', self.default_slugs())


    def build_query(self, case_type=None, filters=None, status=None, owner_ids=None, search_string=None):
        # there's no point doing filters that are like owner_id:(x1 OR x2 OR ... OR x612)
        # so past a certain number just exclude
        owner_ids = owner_ids or []
        MAX_IDS = 50

        def _filter_gen(key, flist):
            if flist and len(flist) < MAX_IDS:
                yield {"terms": {
                    key: [item.lower() if item else "" for item in flist]
                }}

            # demo user hack
            elif flist and "demo_user" not in flist:
                yield {"not": {"term": {key: "demo_user"}}}

        def _domain_term():
            return {"term": {"domain.exact": self.domain}}

        subterms = [_domain_term(), filters] if filters else [_domain_term()]
        if case_type:
            subterms.append({"term": {"type.exact": case_type}})

        if status:
            subterms.append({"term": {"closed": (status == 'closed')}})

        user_filters = list(_filter_gen('owner_id', owner_ids))
        if user_filters:
            subterms.append({'or': user_filters})

        if search_string:
            query_block = {
                "query_string": {"query": search_string}}  # todo, make sure this doesn't suck
        else:
            query_block = {"match_all": {}}

        and_block = {'and': subterms} if subterms else {}

        es_query = {
            'query': {
                'filtered': {
                    'query': query_block,
                    'filter': and_block
                }
            },
            'from': self.config.get('start', 0),
            'size': self.config.get('count', 50)
        }
        if 'sorting_block' in self.config:
            newblock = []
            block = self.config.get('sorting_block')
            defaults = self.default_slugs()
            for pair in block:
                newpair = {}
                for k in pair.keys():
                    if k not in defaults:
                        newkey = '%s.#value' % k
                    else:
                        newkey = k
                    newpair[newkey] = pair[k]
                newblock.append(newpair)
            #es_query['sort'] = self.config.get('sorting_block')
            es_query['sort'] = newblock

        return es_query

    def es_results(self):
        case_type = self.config.get('case_type', None)
        case_status = self.config.get('case_status', None)
        case_owners = self.config.get('case_owners', None)
        search_string = self.config.get('search_string', None)
        case_filter = self.config.get('case_filter', None)

        query = self.build_query(
                        case_type=case_type,
                        filters=case_filter,
                        status=case_status,
                        owner_ids=case_owners,
                        search_string=search_string
                    )

        query_results = self.es.run_query(query)

        if query_results is None or 'hits' not in query_results:
            logging.error("ReportCaseDataSource query error: %s, yielded a result indicating a query error: %s, results: %s" % (
                self.__class__.__name__,
                simplejson.dumps(query),
                simplejson.dumps(query_results)
            ))
            raise RequestFailed
        return query_results

    def get_data(self, slugs=None):
        data = self.es_results()
        for d in data['hits']['hits']:
            if '_source' in d:
                yield restore_property_dict(d['_source'])
            else:
                yield restore_property_dict(d['fields'])
