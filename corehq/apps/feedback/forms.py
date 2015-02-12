from django import forms
from django.utils.translation import ugettext_lazy as _
from bootstrap3_crispy.helper import FormHelper
from bootstrap3_crispy import layout as crispy


class FeedbackForm(forms.Form):

    form = forms.ChoiceField(help_text=_('Form to base performance feedback on.'))
    frequency = forms.ChoiceField(help_text=_('When to send out feedback.'))
    message_template = forms.CharField(
        max_length=200,
        help_text=_('Available template variables are: {user},{Week0},{Week1},{Month0},{Month1}'))

    def __init__(self, *args, **kwargs):
        super(FeedbackForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-sm-3 col-md-2 col-lg-2'
        self.helper.field_class = 'col-sm-9 col-md-8 col-lg-6'
        self.helper.layout = crispy.Layout(
            crispy.Fieldset(
                _("Setup"),
                'form',
                'frequency',
                'message_template',
            ),
        )

