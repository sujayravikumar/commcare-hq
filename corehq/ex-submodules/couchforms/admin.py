from __future__ import absolute_import
from django.contrib import admin
from .models import *


class UnfinishedSubmissionStubAdmin(admin.ModelAdmin):

    model = UnfinishedSubmissionStub
    list_display = [
        'xform_id',
        'timestamp',
        'saved',
        'domain',
    ]

    search_fields = [
        'xform_id',
    ]

    list_filter = [
        'timestamp',
        'saved',
        'domain',
    ]


admin.site.register(UnfinishedSubmissionStub, UnfinishedSubmissionStubAdmin)
