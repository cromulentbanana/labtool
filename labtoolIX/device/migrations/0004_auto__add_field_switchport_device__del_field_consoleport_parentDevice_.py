# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'SwitchPort.device'
        db.add_column('device_switchport', 'device',
                      self.gf('django.db.models.fields.related.ForeignKey')(default=1, to=orm['device.Device']),
                      keep_default=False)

        # Deleting field 'ConsolePort.parentDevice'
        db.delete_column('device_consoleport', 'parentDevice_id')

        # Adding field 'ConsolePort.device'
        db.add_column('device_consoleport', 'device',
                      self.gf('django.db.models.fields.related.ForeignKey')(default=1, to=orm['device.Device']),
                      keep_default=False)

        # Deleting field 'PowerPort.parentDevice'
        db.delete_column('device_powerport', 'parentDevice_id')

        # Adding field 'PowerPort.device'
        db.add_column('device_powerport', 'device',
                      self.gf('django.db.models.fields.related.ForeignKey')(default=1, to=orm['device.Device']),
                      keep_default=False)

        # Removing M2M table for field powerPorts on 'Device'
        db.delete_table('device_device_powerPorts')

        # Removing M2M table for field consolePorts on 'Device'
        db.delete_table('device_device_consolePorts')

        # Removing M2M table for field switchPorts on 'Device'
        db.delete_table('device_device_switchPorts')


    def backwards(self, orm):
        # Deleting field 'SwitchPort.device'
        db.delete_column('device_switchport', 'device_id')


        # User chose to not deal with backwards NULL issues for 'ConsolePort.parentDevice'
        raise RuntimeError("Cannot reverse this migration. 'ConsolePort.parentDevice' and its values cannot be restored.")
        # Deleting field 'ConsolePort.device'
        db.delete_column('device_consoleport', 'device_id')


        # User chose to not deal with backwards NULL issues for 'PowerPort.parentDevice'
        raise RuntimeError("Cannot reverse this migration. 'PowerPort.parentDevice' and its values cannot be restored.")
        # Deleting field 'PowerPort.device'
        db.delete_column('device_powerport', 'device_id')

        # Adding M2M table for field powerPorts on 'Device'
        db.create_table('device_device_powerPorts', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('device', models.ForeignKey(orm['device.device'], null=False)),
            ('powerport', models.ForeignKey(orm['device.powerport'], null=False))
        ))
        db.create_unique('device_device_powerPorts', ['device_id', 'powerport_id'])

        # Adding M2M table for field consolePorts on 'Device'
        db.create_table('device_device_consolePorts', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('device', models.ForeignKey(orm['device.device'], null=False)),
            ('consoleport', models.ForeignKey(orm['device.consoleport'], null=False))
        ))
        db.create_unique('device_device_consolePorts', ['device_id', 'consoleport_id'])

        # Adding M2M table for field switchPorts on 'Device'
        db.create_table('device_device_switchPorts', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('device', models.ForeignKey(orm['device.device'], null=False)),
            ('switchport', models.ForeignKey(orm['device.switchport'], null=False))
        ))
        db.create_unique('device_device_switchPorts', ['device_id', 'switchport_id'])


    models = {
        'device.consoleport': {
            'Meta': {'object_name': 'ConsolePort'},
            'device': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['device.Device']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'portId': ('django.db.models.fields.IntegerField', [], {})
        },
        'device.device': {
            'Meta': {'object_name': 'Device'},
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