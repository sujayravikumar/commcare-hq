from __future__ import absolute_import
import json
from decimal import Decimal
from django.utils.functional import Promise
import six

if six.PY3:
    from django.utils.encoding import force_text
else:
    from django.utils.encoding import force_unicode as force_text


class DecimalEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, Decimal):
            return str(obj)
        return super(DecimalEncoder, self).default(obj)


class LazyEncoder(DecimalEncoder):
    """Taken from https://github.com/tomchristie/django-rest-framework/issues/87
    This makes sure that ugettext_lazy refrences in a dict are properly evaluated
    """

    def default(self, obj):
        if isinstance(obj, Promise):
            return force_text(obj)
        return super(LazyEncoder, self).default(obj)
