# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'Reservation.extends'
        db.alter_column('reservation_reservation', 'extends_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['reservation.Reservation'], null=True))

    def backwards(self, orm):

        # Changing field 'Reservation.extends'
        db.alter_column('reservation_reservation', 'extends_id', self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['reservation.Reservation']))

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
        },
        'reservation.reservation': {
            'Meta': {'object_name': 'Reservation'},
            'comment': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'devices': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['device.Device']", 'symmetrical': 'False'}),
            'endTime': ('django.db.models.fields.DateTimeField', [], {}),
            'extends': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': "orm['reservation.Reservation']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'startTime': ('django.db.models.fields.DateTimeField', [], {}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        }
    }

    complete_apps = ['reservation']