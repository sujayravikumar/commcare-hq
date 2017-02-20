from __future__ import absolute_import
from django import forms
from corehq.apps.groups.models import Group


class GroupField(forms.ChoiceField):

    def __init__(self, domain, *args, **kwargs):
        self.domain = domain
        groups = Group.by_domain(self.domain)
        super(GroupField, self).__init__(
            choices=[(group._id, group.display_name) for group in groups],
            *args, **kwargs
        )
