# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'GuidedTour'
        db.create_table(u'tour_guidedtour', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('slug', self.gf('django.db.models.fields.CharField')(unique=True, max_length=25, db_index=True)),
            ('area', self.gf('django.db.models.fields.CharField')(max_length=25, db_index=True)),
            ('start_url_name', self.gf('django.db.models.fields.CharField')(max_length=25, blank=True)),
            ('start_url_args', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('start_url_kwargs', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('auto_add_to_new_users', self.gf('django.db.models.fields.BooleanField')(default=True, db_index=True)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal(u'tour', ['GuidedTour'])

        # Adding model 'QueuedTour'
        db.create_table(u'tour_queuedtour', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('web_user', self.gf('django.db.models.fields.CharField')(max_length=80, db_index=True)),
            ('domain', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=256, null=True, blank=True)),
            ('tour', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['tour.GuidedTour'])),
            ('is_active', self.gf('django.db.models.fields.BooleanField')(default=True, db_index=True)),
            ('furthest_step', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('date_created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('date_modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('date_completed', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'tour', ['QueuedTour'])


    def backwards(self, orm):
        
        # Deleting model 'GuidedTour'
        db.delete_table(u'tour_guidedtour')

        # Deleting model 'QueuedTour'
        db.delete_table(u'tour_queuedtour')


    models = {
        u'tour.guidedtour': {
            'Meta': {'object_name': 'GuidedTour'},
            'area': ('django.db.models.fields.CharField', [], {'max_length': '25', 'db_index': 'True'}),
            'auto_add_to_new_users': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'db_index': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'slug': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '25', 'db_index': 'True'}),
            'start_url_args': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'start_url_kwargs': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'start_url_name': ('django.db.models.fields.CharField', [], {'max_length': '25', 'blank': 'True'})
        },
        u'tour.queuedtour': {
            'Meta': {'object_name': 'QueuedTour'},
            'date_completed': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'domain': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'furthest_step': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'db_index': 'True'}),
            'tour': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['tour.GuidedTour']"}),
            'web_user': ('django.db.models.fields.CharField', [], {'max_length': '80', 'db_index': 'True'})
        }
    }

    complete_apps = ['tour']
