from dimagi.utils.decorators.memoized import memoized
from django.conf import settings
from django.utils.translation import ugettext_noop
from django.utils.translation import ugettext as _
from corehq.apps.reports.datatables import DataTablesColumn, DataTablesHeader
from corehq.apps.reports.fields import SelectMobileWorkerField
from corehq.apps.reports.generic import GenericTabularReport, ElasticProjectInspectionReport
from corehq.apps.reports.standard import ProjectReportParametersMixin, ProjectReport
from corehq.apps.reports.standard.cases.data_sources import ReportCaseDataSource


class AdvancedCaseList(ElasticProjectInspectionReport, ProjectReport, ProjectReportParametersMixin):
    name = ugettext_noop('Advanced Case List')
    slug = 'case_list_adv'
    ajax_pagination = True
    asynchronous = True

    fields = [
        'corehq.apps.reports.fields.FilterUsersField',
        'corehq.apps.reports.fields.AdvancedSelectCaseOwnerField',
        'corehq.apps.reports.fields.CaseTypeField',
        'corehq.apps.reports.fields.SelectOpenCloseField',
        'corehq.apps.reports.standard.cases.filters.CaseSearchFilter',
        'corehq.apps.reports.standard.cases.filters.CasePropertiesFilter',
    ]


    @property
    def shared_pagination_GET_params(self):
        shared_params = super(AdvancedCaseList, self).shared_pagination_GET_params
        return shared_params

    @property
    def rendered_report_title(self):
        if not self.individual:
            self.name = _("%(report_name)s for %(worker_type)s") % {
                "report_name": _(self.name),
                "worker_type": _(SelectMobileWorkerField.get_default_text(self.user_filter))
            }
        return self.name


    @classmethod
    def show_in_navigation(cls, domain=None, project=None, user=None):
        if domain in settings.ES_CASE_FULL_INDEX_DOMAINS:
            return True
        else:
            return False

    @property
    def headers(self):
        case_properties = self.case_properties()
        if case_properties:
            headers = DataTablesHeader(*[DataTablesColumn(x, prop_name=x) for x in case_properties])
            return headers
        else:
            return self.standard_headers

    @property
    def standard_headers(self):
        headers = DataTablesHeader(
            DataTablesColumn(_("Case Type"), prop_name="type.exact"),
            DataTablesColumn(_("Name"), prop_name="name.exact"),
            DataTablesColumn(_("Owner"), prop_name="owner_display", sortable=False),
            DataTablesColumn(_("Created Date"), prop_name="opened_on"),
            DataTablesColumn(_("Created By"), prop_name="opened_by_display", sortable=False),
            DataTablesColumn(_("Modified Date"), prop_name="modified_on"),
            DataTablesColumn(_("Status"), prop_name="get_status_display", sortable=False)
        )
        headers.custom_sort = [[5, 'desc']]
        return headers


    def case_properties(self):
        prop_query = self.request.GET.get('property_query', '')
        if prop_query:
            return [x.strip() for x in self.request.GET.get('property_query', "").split(',')]
        else:
            return None

    @memoized
    def report_case_data(self, data_source):
        if getattr(self, 'case_data', None) is None:
            self.case_data = list(data_source.get_data())
        return self.case_data

    @property
    def total_records(self):
        """
            Override for pagination slice from ES
            Returns an integer.
        """
        es_res = self.data_source.es_results()
        if es_res is not None:
            return es_res['hits'].get('total', 0)
        else:
            return 0


    @property
    def data_source(self):
        case_properties = self.case_properties()

        config = {
            'domain': self.domain,
        }
        if case_properties:
            config['case_properties'] = case_properties
        sorting_block = self.get_sorting_block()
        if sorting_block:
            config['sorting_block'] = sorting_block

        data_source = ReportCaseDataSource(config)
        return data_source


    @property
    def rows(self):
        def fmt(val, formatter=lambda k: k, default=u'\u2014'):
            return formatter(val) if val is not None else default
        print "rows!"

        cols = self.data_source.slugs()
        for row in self.report_case_data(self.data_source):
            yield [fmt(row.get(col, '---')) for col in cols]

