# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'Device.console'
        db.alter_column('device_device', 'console_id', self.gf('django.db.models.fields.related.OneToOneField')(unique=True, null=True, to=orm['device.ConsolePort']))
        # Adding unique constraint on 'Device', fields ['name']
        db.create_unique('device_device', ['name'])


        # Changing field 'Device.power'
        db.alter_column('device_device', 'power_id', self.gf('django.db.models.fields.related.OneToOneField')(unique=True, null=True, to=orm['device.PowerPort']))

    def backwards(self, orm):
        # Removing unique constraint on 'Device', fields ['name']
        db.delete_unique('device_device', ['name'])


        # Changing field 'Device.console'
        db.alter_column('device_device', 'console_id', self.gf('django.db.models.fields.related.OneToOneField')(default=None, unique=True, to=orm['device.ConsolePort']))

        # Changing field 'Device.power'
        db.alter_column('device_device', 'power_id', self.gf('django.db.models.fields.related.OneToOneField')(default=None, unique=True, to=orm['device.PowerPort']))

    models = {
        'device.consoleport': {
            'Meta': {'object_name': 'ConsolePort'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'parentDevice': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['device.Device']"}),
            'portId': ('django.db.models.fields.IntegerField', [], {})
        },
        'device.device': {
            'Meta': {'object_name': 'Device'},
            'comment': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'console': ('django.db.models.fields.related.OneToOneField', [], {'blank': 'True', 'related_name': "'consolidatesDevice'", 'unique': 'True', 'null': 'True', 'to': "orm['device.ConsolePort']"}),
            'consolePorts': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['device.ConsolePort']", 'symmetrical': 'False', 'blank': 'True'}),
            'deviceClasses': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['device.DeviceClass']", 'symmetrical': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            'power': ('django.db.models.fields.related.OneToOneField', [], {'blank': 'True', 'related_name': "'powersDevice'", 'unique': 'True', 'null': 'True', 'to': "orm['device.PowerPort']"}),
            'powerPorts': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['device.PowerPort']", 'symmetrical': 'False', 'blank': 'True'}),
            'switchPorts': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['device.SwitchPort']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'device.deviceclass': {
            'Meta': {'object_name': 'DeviceClass'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'device.link': {
            'Meta': {'object_name': 'Link'},
            'comment': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'switchPortA': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'linkA_set'", 'to': "orm['device.SwitchPort']"}),
            'switchPortB': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'linkB_set'", 'to': "orm['device.SwitchPort']"})
        },
        'device.powerport': {
            'Meta': {'object_name': 'PowerPort'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'parentDevice': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['device.Device']"}),
            'socketId': ('django.db.models.fields.IntegerField', [], {})
        },
        'device.switchport': {
            'Meta': {'object_name': 'SwitchPort'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mac': ('django.db.models.fields.CharField', [], {'max_length': '21'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'vlans': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['device.Vlan']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'device.vlan': {
            'Meta': {'object_name': 'Vlan'},
            'comment': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'number': ('django.db.models.fields.IntegerField', [], {})
        }
    }

    complete_apps = ['device']