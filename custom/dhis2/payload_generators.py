from datetime import date
import json

from django.conf import settings

from casexml.apps.case.models import CommCareCase
from corehq.apps.receiverwrapper.models import FormRepeater, RegisterGenerator
from corehq.apps.receiverwrapper.repeater_generators import BasePayloadGenerator
from custom.dhis2.models import Dhis2Api
from custom.dhis2.tasks import NUTRITION_ASSESSMENT_FIELDS, RISK_ASSESSMENT_FIELDS


@RegisterGenerator(FormRepeater, 'dhis2_nutrition_assessment_event_json', 'Default JSON', is_default=True)
class FormRepeaterDhis2NutritionAssessmentEventPayloadGenerator(BasePayloadGenerator):
    def get_payload(self, repeat_record, form):
        dhis2_api = Dhis2Api(settings.DHIS2_HOST, settings.DHIS2_USERNAME, settings.DHIS2_PASSWORD)
        nutrition_id = dhis2_api.get_program_id('Pediatric Nutrition Assessment')
        event = dhis2_api.form_to_event(nutrition_id, form, NUTRITION_ASSESSMENT_FIELDS)
        return json.dumps(event)


@RegisterGenerator(FormRepeater, 'dhis2_risk_assessment_event_json', 'Default JSON', is_default=True)
class FormRepeaterDhis2RiskAssessmentEventPayloadGenerator(BasePayloadGenerator):
    def get_payload(self, repeat_record, form):
        dhis2_api = Dhis2Api(settings.DHIS2_HOST, settings.DHIS2_USERNAME, settings.DHIS2_PASSWORD)
        risk_id = dhis2_api.get_program_id('Underlying Risk Assessment')
        # Check whether the case needs to be enrolled in the Risk Assessment Program
        cases = CommCareCase.get_by_xform_id(form.get_id)
        if len(cases) != 1:
            # TODO: Do something
            pass
        case = cases[0]
        if not dhis2_api.enrolled_in(case['external_id'], 'Child', 'Underlying Risk Assessment'):
            today = date.today().strftime('%Y-%m-%d')
            program_data = {
                'Household Number': case['mother_id'],
                'Name of Mother/Guardian': case['mother_first_name'],
                'GN Division of Household': case['gn'],
            }
            # TODO: Will external ID be set?
            dhis2_api.enroll_in_id(case['external_id'], risk_id, today, program_data)
        event = dhis2_api.form_to_event(risk_id, form, RISK_ASSESSMENT_FIELDS)
        return json.dumps(event)
