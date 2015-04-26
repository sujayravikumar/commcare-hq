from collections import namedtuple
from jsonobject import JsonObject
from corehq.apps.userreports.specs import TypeProperty
from dimagi.utils.decorators.memoized import memoized


class AbtSupervisorExpressionSpec(JsonObject):
    type = TypeProperty('abt_supervisor')

    @property
    @memoized
    def _flag_specs(self):
        """
        Return a dict where keys are form xmlns and values are lists of FlagSpecs
        """
        FlagSpec = namedtuple("FlagSpec", [
            "path",
            "danger_value", # empty list is a sentinal that means any answer
            "warning_string",
            "warning_property_path"
        ])
        return {
            # # Form 2
            # "http://openrosa.org/formdesigner/BBBA67FC-4E25-46B4-AB64-56F820D48A9E": [
            #     FlagSpec(
            #         path=['q1_action'],
            #         danger_value=[],
            #         warning_string="Problem noted: Vehicle(s) or driver(s) do(es) not possess the required certificate or license. Vehicle or driver cannot be used until certificate is obtained.",
            #         warning_property_path=None
            #     ),
            # ],
            # Form 3
            "http://openrosa.org/formdesigner/54338047-CFB6-4D5B-861B-2256A10BBBC8": [
                FlagSpec(
                    path=["q2_action"],
                    danger_value=[],
                    warning_string="Problem reported: Spray operator(s) not properly fed or hydrated prior to donning PPE.",
                    warning_property_path=None,
                ),
            ]
        }

        # [
        #     FlagSpec(
        #         form_xmlns="http://openrosa.org/formdesigner/BB2BF979-BD8F-4B8D-BCF8-A46451228BA9",
        #         path=["q2"],
        #         danger_value="No",
        #         warning_string="The nearest sensitive receptor is {msg} meters away",
        #         warning_property_path=['q2_next']
        #     ),
        #     FlagSpec(
        #         form_xmlns="http://openrosa.org/formdesigner/BB2BF979-BD8F-4B8D-BCF8-A46451228BA9",
        #         path=["q5"],
        #         danger_value="No",
        #         warning_string="The leak will be repaired on {msg}",
        #         warning_property_path=['q5_action_two']
        #     ),
        #     FlagSpec(
        #         form_xmlns="dummy",
        #         path=["dummy"],
        #         danger_value="dummy",
        #         warning_string="foo{msg}",
        #         warning_property_path=['bloop']
        #     ),
        #     FlagSpec(
        #         form_xmlns="http://openrosa.org/formdesigner/54338047-CFB6-4D5B-861B-2256A10BBBC8",
        #         path=["q2"],
        #         danger_value="No",
        #         warning_string="{msg}",
        #         warning_property_path=['nothing_pls']
        #     )
        # ]

    @classmethod
    def _get_val(cls, item, path):
        if path:
            try:
                v = item['form']
                for key in path:
                    v = v[key]
                return v
            except KeyError:
                return None

    def __call__(self, item, context=None):
        """
        Given a document (item), return a list of documents representing each
        of the flagged questions.
        """

        docs = []
        for spec in self._flag_specs.get(item['xmlns'], []):
            if (
                self._get_val(item, spec.path) == spec.danger_value or
                spec.danger_value == [] # [] is a sentinel meaning any value should raise the flag
            ):
                docs.append({
                    'flag': spec.path[-1],
                    'warning': spec.warning_string.format(
                        msg=self._get_val(item, spec.warning_property_path) or ""
                    )
                })
        return docs


def abt_supervisor_expression(spec, context):
    wrapped = AbtSupervisorExpressionSpec.wrap(spec)
    return wrapped
