# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from __future__ import absolute_import
from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounting', '0023__simplify__credit_line__product_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subscriptionadjustment',
            name='date_created',
            field=models.DateTimeField(auto_now_add=True),
            preserve_default=True,
        ),
    ]
