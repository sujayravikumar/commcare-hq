from custom.opm.opm_reports.fake_conditions_met import DuplicateConditionsMet
from corehq.apps.hqcase.utils import get_cases_in_domain
from dimagi.utils.decorators.memoized import memoized
import datetime

from corehq.apps.users.models import CommCareCase

CASE_INDEX_BY_AWC = {}

PREGNANCY_APP_CMR = {
	4: "window_1_1",
	5: "window_1_2",
	6: "window_1_3",	
	7: "window_2_1",	
	8: "window_2_2",	
	9: "window_2_3",	
}

MOTHER_APP_CMR = {
	1: "window3_child1",
	2: "window4_child1",
	3: "window5_child1",
	4: "window6_child1",
	5: "window7_child1",
	6: "window8_child1",
	7: "window9_child1",
	8: "window10_child1",
	9: "window11_child1",
	10: "window12_child1",
	11: "window13_child1",
	12: "window14_child1",
}

def prepare_case_index():
	cases = get_cases_in_domain("opm", type="Pregnancy")
	cases = list(cases)
	for case in cases:
		awc = case["awc_name"] if "awc_name" in case else "---"
		if CASE_INDEX_BY_AWC.has_key(awc):
			CASE_INDEX_BY_AWC[awc].append(case)
		else:
			CASE_INDEX_BY_AWC[awc] = []

class AppCMR(DuplicateConditionsMet):

	def __init__(self, case, report):
		super(AppCMR, self).__init__({"_source":{"_id":case["_id"]}}, report)
		self.app_met_or_not = None
		self.app_cmr_matches = False
		self.window_name = None
		self.case = case

	def cmr_from_form(self, window_x_y):
		forms = self.forms
		window_x_y_in_forms = [form.form[window_x_y] for form in forms if window_x_y in form.form]
		return None if len(window_x_y_in_forms) is 0 else '1' in window_x_y_in_forms

	@property
	@memoized
	def met_from_app(self):
		all_window_X_Ys = PREGNANCY_APP_CMR.values() + MOTHER_APP_CMR.values()
		met = {x: None for x in all_window_X_Ys}
		case = self.case
		for window_x_y in all_window_X_Ys:
			met_or_not = '1' in case[window_x_y] if window_x_y in case else "--"
			if met_or_not is "--":
				met_or_not = self.cmr_from_form(window_x_y)
			met[window_x_y] = met_or_not
		return met

	def set_app_met_or_not(self):
		status = self.status
		preg_month = self.preg_month
		child_age = self.child_age
		window = self.window
		if status == "pregnant":
			self.window_name = PREGNANCY_APP_CMR[preg_month]
			self.app_met_or_not = self.met_from_app[PREGNANCY_APP_CMR[preg_month]]
		elif status == "mother":
			if child_age % 3 != 0:
				self.app_met_or_not = "vhnd_check"
				self.window_name = "vhnd_check"
			else:
				self.window_name = MOTHER_APP_CMR[window]
				self.app_met_or_not = self.met_from_app[MOTHER_APP_CMR[window]]
		self.app_cmr_matches = self.app_met_or_not == self.met_or_not

class QARunner(object):
	def __init__(self, filters, filename="None"):
		self.filters = filters

	def get_report_object(self):
		filters = self.filters
		startdate = datetime.datetime(filters["year"], filters["month"], 1)
		enddate = startdate + datetime.timedelta(30)
		obj = type('report', (object,),{
				"snapshot": None,
				"month": filters["month"],
				"year": filters["year"],
				"datespan": type('datespan', (object,), {"startdate": startdate, "enddate":enddate})(),
				"block": filters["block"]
			})()
		return obj

	def get_case_list(self, for_all_cases=False):
		if not for_all_cases:
			return CASE_INDEX_BY_AWC[self.filters["awc"]]
		else:
			case_lists_by_awc = CASE_INDEX_BY_AWC.values()
			case_list = []
			for _list in case_lists_by_awc:
				case_list = case_list + _list
			return case_list

	def filename_from_filters(self, for_all_cases=False):
		fil = lambda x: self.filters[x]
		return "/home/sravfeyn/OPM_QA/%s-%s-%s-%s-%s.csv" % ("all-cases" if for_all_cases else fil("awc"), fil("month"), fil("year"), fil("block"), datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

	def run_qa(self, filename=None, for_all_cases=False):
		filename = filename or self.filename_from_filters(for_all_cases=for_all_cases)
		_file = open(filename, 'w')
		report = self.get_report_object()
		_file.write("case-id, awc_name, name, dod, edd,status,preg_month,child_age,met_or_not,app_met_or_not,app_cmr_matches, window-property\n")
		for case in self.get_case_list(for_all_cases=for_all_cases):
			cmr = None
			try:
				cmr = AppCMR(case, report)
				cmr.set_app_met_or_not()
			except:
				pass
			if not cmr:
				continue
			row = "%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s\n" % (
				cmr.case_id,
				cmr.awc_name, 
				cmr.name, 
				cmr.dod, 
				cmr.edd,
				cmr.status,
				cmr.preg_month,
				cmr.child_age,
				cmr.met_or_not,
				cmr.app_met_or_not,
				cmr.app_cmr_matches,
				cmr.window_name
			)
			_file.write(row.encode("utf-8"))
		_file.close()
		return filename

def sample_test(for_all_cases=False):
	filters = {"month":2, "year":2014, "block":"atri", "awc":"Pathri"}
	prepare_case_index()
	awcs = CASE_INDEX_BY_AWC.keys()
	QAR = QARunner(filters)
	QAR.run_qa(for_all_cases=for_all_cases)