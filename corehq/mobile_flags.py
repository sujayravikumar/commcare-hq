from __future__ import absolute_import
from collections import namedtuple


MobileFlag = namedtuple('MobileFlag', 'slug label')


MULTIPLE_APPS_UNLIMITED = MobileFlag(
    'multiple_apps_unlimited',
    'Enable unlimited multiple apps'
)
