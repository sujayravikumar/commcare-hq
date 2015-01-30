import json

from crispy_forms import layout as crispy
from crispy_forms.bootstrap import StrictButton
from crispy_forms.helper import FormHelper
from django.contrib.auth.forms import AuthenticationForm
from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _


class EmailAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(label=_("E-mail"), max_length=75)

    def clean_username(self):
        username = self.cleaned_data['username'].lower()
        return username


class CloudCareAuthenticationForm(EmailAuthenticationForm):
    username = forms.EmailField(label=_("Username"), max_length=75)


class BulkUploadForm(forms.Form):
    bulk_upload_file = forms.FileField(label="")
    action = forms.CharField(widget=forms.HiddenInput(), initial='bulk_upload')

    def __init__(self, plural_noun, action, form_id, *args, **kwargs):
        super(BulkUploadForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = form_id
        self.helper.form_method = 'post'
        if action:
            self.helper.form_action = action
        self.helper.layout = crispy.Layout(
            crispy.Fieldset(
                "",
                crispy.Field(
                    'bulk_upload_file',
                    data_bind="value: file",
                ),
                crispy.Field(
                    'action',
                ),
            ),
            StrictButton(
                ('<i class="icon-cloud-upload"></i> Upload %s'
                 % plural_noun.title()),
                css_class='btn-primary',
                data_bind='disable: !file()',
                onclick='this.disabled=true;this.form.submit();',
                type='submit',
            ),
        )


class FormListForm(forms.Form):
    """
    A higher-level form for editing an arbitrary number of instances of one
    sub-form in a tabular fashion.
    Give your child_form_class a `slug` field to enforce uniqueness

    API:
        is_valid
        cleaned_data
        errors
    """
    child_form_class = None  # Django form which controls each row
    sortable = False
    can_add_elements = False

    child_form_data = forms.CharField(widget=forms.HiddenInput)

    def __init__(self, data=None, *args, **kwargs):
        if self.child_form_class is None:
            raise NotImplementedError("You must specify a child form to use"
                                      "for each row")
        self.sub_forms = []
        for row in data:
            self.sub_forms.append(self.child_form_class(row))
        super(FormListForm, self).__init__(data=data, *args, **kwargs)

    def verify_no_duplicates(self, child_form_data):
        errors = set()
        slugs = [form_data['slug'].lower()
                 for form_data in child_form_data if 'slug' in form_data]
        for slug in slugs:
            if slugs.count(slug) > 1:
                errors.add(_("Key '{}' was duplicated, key names must be "
                             "unique.").format(slug))
        return errors

    def clean_child_forms(self):
        raw_child_form_data = json.loads(self.cleaned_data['child_form_data'])
        errors = set()
        cleaned_data = []
        for raw_child_form in raw_child_form_data:
            child_form = self.child_form_class(raw_child_form)
            child_form.is_valid()
            cleaned_data.append(child_form.cleaned_data)
            if child_form.errors:
                errors.update([error[0]
                               for error in child_form.errors.values()])

        errors.update(self.verify_no_duplicates(cleaned_data))

        if errors:
            raise ValidationError('<br/>'.join(sorted(errors)))

        return cleaned_data
