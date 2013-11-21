from django.conf import settings
from django.utils.translation import ugettext_noop
from django.utils.translation import ugettext as _
from corehq.apps.reports.api import ReportDataSource
from corehq.apps.reports.fields import SelectMobileWorkerField
from corehq.apps.reports.standard.cases.basic import CaseListMixin
from corehq.apps.reports.standard.inspect import ProjectInspectionReport
from dimagi.utils.decorators.memoized import memoized



class AdvancedCaseList(ProjectInspectionReport, ReportDataSource):

    # note that this class is not true to the spirit of ReportDataSource; the whole
    # point is the decouple generating the raw report data from the report view/django
    # request. but currently these are too tightly bound to decouple

    name = ugettext_noop('Advanced Case List')
    slug = 'case_list_adv'

    @property
    @memoized
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
