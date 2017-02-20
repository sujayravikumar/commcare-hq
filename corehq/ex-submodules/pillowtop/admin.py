from __future__ import absolute_import
from django.contrib import admin
from .models import *


class PillowCheckpointAdmin(admin.ModelAdmin):

    model = DjangoPillowCheckpoint
    list_display = [
        'checkpoint_id',
        'timestamp',
        'sequence',
    ]


admin.site.register(DjangoPillowCheckpoint, PillowCheckpointAdmin)

