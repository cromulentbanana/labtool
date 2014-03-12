# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Bootmode'
        db.create_table('device_bootmode', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=100)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('device', ['Bootmode'])

        # Adding M2M table for field deviceClasses on 'Bootmode'
        db.create_table('device_bootmode_deviceClasses', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('bootmode', models.ForeignKey(orm['device.bootmode'], null=False)),
            ('deviceclass', models.ForeignKey(orm['device.deviceclass'], null=False))
        ))
        db.create_unique('device_bootmode_deviceClasses', ['bootmode_id', 'deviceclass_id'])

        # Adding field 'Device.bootmode'
        db.add_column('device_device', 'bootmode',
                      self.gf('django.db.models.fields.related.OneToOneField')(blank=True, related_name='bootMode', unique=True, null=True, to=orm['device.Bootmode']),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting model 'Bootmode'
        db.delete_table('device_bootmode')

        # Removing M2M table for field deviceClasses on 'Bootmode'
        db.delete_table('device_bootmode_deviceClasses')

        # Deleting field 'Device.bootmode'
        db.delete_column('device_device', 'bootmode_id')


    models = {
        'device.bootmode': {
            'Meta': {'object_name': 'Bootmode'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'deviceClasses': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['device.DeviceClass']", 'symmetrical': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'})
        },
        'device.consoleport': {
            'Meta': {'object_name': 'ConsolePort'},
            'device': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['device.Device']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'portId': ('django.db.models.fields.IntegerField', [], {})
        },
        'device.device': {
            'Meta': {'object_name': 'Device'},
            'bootmode': ('django.db.models.fields.related.OneToOneField', [], {'blank': 'True', 'related_name': "'bootMode'", 'unique': 'True', 'null': 'True', 'to': "orm['device.Bootmode']"}),
            'comment': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'console': ('django.db.models.fields.related.OneToOneField', [], {'blank': 'True', 'related_name': "'consolidatesDevice'", 'unique': 'True', 'null': 'True', 'to': "orm['device.ConsolePort']"}),
            'deviceClasses': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['device.DeviceClass']", 'symmetrical': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            'power': ('django.db.models.fields.related.OneToOneField', [], {'blank': 'True', 'related_name': "'powersDevice'", 'unique': 'True', 'null': 'True', 'to': "orm['device.PowerPort']"})
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
            'device': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['device.Device']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'socketId': ('django.db.models.fields.IntegerField', [], {})
        },
        'device.switchport': {
            'Meta': {'object_name': 'SwitchPort'},
            'device': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['device.Device']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mac': ('django.db.models.fields.CharField', [], {'max_length': '21', 'blank': 'True'}),
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