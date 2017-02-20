from __future__ import absolute_import
from corehq.preindex import ExtraPreindexPlugin
from django.conf import settings

ExtraPreindexPlugin.register('phone', __file__, (None, settings.SYNCLOGS_DB))
