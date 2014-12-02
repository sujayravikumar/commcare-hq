# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'LocationAccess'
        db.create_table(u'locations_locationaccess', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user_id', self.gf('django.db.models.fields.CharField')(max_length=255, db_index=True)),
            ('sql_location', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['locations.SQLLocation'], null=True)),
        ))
        db.send_create_signal(u'locations', ['LocationAccess'])


    def backwards(self, orm):
        
        # Deleting model 'LocationAccess'
        db.delete_table(u'locations_locationaccess')


    models = {
        u'locations.locationaccess': {
            'Meta': {'object_name': 'LocationAccess'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'sql_location': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['locations.SQLLocation']", 'null': 'True'}),
            'user_id': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'})
        },
        u'locations.sqllocation': {
            'Meta': {'unique_together': "(('domain', 'site_code'),)", 'object_name': 'SQLLocation'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'domain': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'}),
            'external_id': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_archived': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'latitude': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '20', 'decimal_places': '10'}),
            u'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            u'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'location_id': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100', 'db_index': 'True'}),
            'location_type': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'longitude': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '20', 'decimal_places': '10'}),
            'metadata': ('json_field.fields.JSONField', [], {'default': '{}'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True'}),
            'parent': ('mptt.fields.TreeForeignKey', [], {'blank': 'True', 'related_name': "'children'", 'null': 'True', 'to': u"orm['locations.SQLLocation']"}),
            u'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'site_code': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'supply_point_id': ('django.db.models.fields.CharField', [], {'max_length': '255', 'unique': 'True', 'null': 'True', 'db_index': 'True'}),
            u'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'})
        }
    }

    complete_apps = ['locations']
