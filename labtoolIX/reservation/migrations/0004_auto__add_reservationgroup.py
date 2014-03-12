# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'ReservationGroup'
        db.create_table(u'reservation_reservationgroup', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('reservation_time', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal(u'reservation', ['ReservationGroup'])

        # Adding M2M table for field reservable_classes on 'ReservationGroup'
        db.create_table(u'reservation_reservationgroup_reservable_classes', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('reservationgroup', models.ForeignKey(orm[u'reservation.reservationgroup'], null=False)),
            ('deviceclass', models.ForeignKey(orm[u'device.deviceclass'], null=False))
        ))
        db.create_unique(u'reservation_reservationgroup_reservable_classes', ['reservationgroup_id', 'deviceclass_id'])


    def backwards(self, orm):
        # Deleting model 'ReservationGroup'
        db.delete_table(u'reservation_reservationgroup')

        # Removing M2M table for field reservable_classes on 'ReservationGroup'
        db.delete_table('reservation_reservationgroup_reservable_classes')


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'device.bootmode': {
            'Meta': {'object_name': 'Bootmode'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'deviceClasses': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['device.DeviceClass']", 'symmetrical': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_destructive': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'})
        },
        u'device.consoleport': {
            'Meta': {'object_name': 'ConsolePort'},
            'device': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['device.Device']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'portId': ('django.db.models.fields.IntegerField', [], {})
        },
        u'device.device': {
            'Meta': {'object_name': 'Device'},
            'bootmode': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['device.Bootmode']", 'null': 'True', 'blank': 'True'}),
            'comment': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'console': ('django.db.models.fields.related.OneToOneField', [], {'blank': 'True', 'related_name': "'consolidatesDevice'", 'unique': 'True', 'null': 'True', 'to': u"orm['device.ConsolePort']"}),
            'deviceClasses': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['device.DeviceClass']", 'symmetrical': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            'power': ('django.db.models.fields.related.OneToOneField', [], {'blank': 'True', 'related_name': "'powersDevice'", 'unique': 'True', 'null': 'True', 'to': u"orm['device.PowerPort']"})
        },
        u'device.deviceclass': {
            'Meta': {'object_name': 'DeviceClass'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'device.powerport': {
            'Meta': {'object_name': 'PowerPort'},
            'device': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['device.Device']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'socketId': ('django.db.models.fields.IntegerField', [], {})
        },
        u'reservation.reservation': {
            'Meta': {'object_name': 'Reservation'},
            'comment': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'devices': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['device.Device']", 'symmetrical': 'False'}),
            'endTime': ('django.db.models.fields.DateTimeField', [], {}),
            'extends': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': u"orm['reservation.Reservation']", 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'startTime': ('django.db.models.fields.DateTimeField', [], {}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        u'reservation.reservationgroup': {
            'Meta': {'object_name': 'ReservationGroup'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'reservable_classes': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['device.DeviceClass']", 'symmetrical': 'False'}),
            'reservation_time': ('django.db.models.fields.IntegerField', [], {})
        }
    }

    complete_apps = ['reservation']