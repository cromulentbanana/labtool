# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Reservation'
        db.create_table('reservation_reservation', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('extends', self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['reservation.Reservation'], blank=True)),
            ('comment', self.gf('django.db.models.fields.TextField')()),
            ('startTime', self.gf('django.db.models.fields.DateTimeField')()),
            ('endTime', self.gf('django.db.models.fields.DateTimeField')()),
        ))
        db.send_create_signal('reservation', ['Reservation'])

        # Adding M2M table for field devices on 'Reservation'
        db.create_table('reservation_reservation_devices', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('reservation', models.ForeignKey(orm['reservation.reservation'], null=False)),
            ('device', models.ForeignKey(orm['device.device'], null=False))
        ))
        db.create_unique('reservation_reservation_devices', ['reservation_id', 'device_id'])


    def backwards(self, orm):
        # Deleting model 'Reservation'
        db.delete_table('reservation_reservation')

        # Removing M2M table for field devices on 'Reservation'
        db.delete_table('reservation_reservation_devices')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'device.consoleport': {
            'Meta': {'object_name': 'ConsolePort'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'parentDevice': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['device.Device']"}),
            'portId': ('django.db.models.fields.IntegerField', [], {})
        },
        'device.device': {
            'Meta': {'object_name': 'Device'},
            'comment': ('django.db.models.fields.TextField', [], {}),
            'console': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'consolidatesDevice'", 'unique': 'True', 'blank': 'True', 'to': "orm['device.ConsolePort']"}),
            'consolePorts': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['device.ConsolePort']", 'symmetrical': 'False'}),
            'deviceClasses': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['device.DeviceClass']", 'symmetrical': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'power': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'powersDevice'", 'unique': 'True', 'blank': 'True', 'to': "orm['device.PowerPort']"}),
            'powerPorts': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['device.PowerPort']", 'symmetrical': 'False'}),
            'switchPorts': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['device.SwitchPort']", 'symmetrical': 'False'})
        },
        'device.deviceclass': {
            'Meta': {'object_name': 'DeviceClass'},
            'description': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
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
            'vlans': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['device.Vlan']", 'symmetrical': 'False'})
        },
        'device.vlan': {
            'Meta': {'object_name': 'Vlan'},
            'comment': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'number': ('django.db.models.fields.IntegerField', [], {})
        },
        'reservation.reservation': {
            'Meta': {'object_name': 'Reservation'},
            'comment': ('django.db.models.fields.TextField', [], {}),
            'devices': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['device.Device']", 'symmetrical': 'False'}),
            'endTime': ('django.db.models.fields.DateTimeField', [], {}),
            'extends': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': "orm['reservation.Reservation']", 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'startTime': ('django.db.models.fields.DateTimeField', [], {}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        }
    }

    complete_apps = ['reservation']