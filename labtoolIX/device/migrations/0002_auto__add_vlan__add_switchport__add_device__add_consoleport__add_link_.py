# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Vlan'
        db.create_table('device_vlan', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('number', self.gf('django.db.models.fields.IntegerField')()),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('comment', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('device', ['Vlan'])

        # Adding model 'SwitchPort'
        db.create_table('device_switchport', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('mac', self.gf('django.db.models.fields.CharField')(max_length=21)),
        ))
        db.send_create_signal('device', ['SwitchPort'])

        # Adding M2M table for field vlans on 'SwitchPort'
        db.create_table('device_switchport_vlans', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('switchport', models.ForeignKey(orm['device.switchport'], null=False)),
            ('vlan', models.ForeignKey(orm['device.vlan'], null=False))
        ))
        db.create_unique('device_switchport_vlans', ['switchport_id', 'vlan_id'])

        # Adding model 'Device'
        db.create_table('device_device', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('model', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('comment', self.gf('django.db.models.fields.TextField')()),
            ('power', self.gf('django.db.models.fields.related.OneToOneField')(related_name='powersDevice', unique=True, blank=True, to=orm['device.PowerPort'])),
            ('console', self.gf('django.db.models.fields.related.OneToOneField')(related_name='consolidatesDevice', unique=True, blank=True, to=orm['device.ConsolePort'])),
        ))
        db.send_create_signal('device', ['Device'])

        # Adding M2M table for field deviceClasses on 'Device'
        db.create_table('device_device_deviceClasses', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('device', models.ForeignKey(orm['device.device'], null=False)),
            ('deviceclass', models.ForeignKey(orm['device.deviceclass'], null=False))
        ))
        db.create_unique('device_device_deviceClasses', ['device_id', 'deviceclass_id'])

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

        # Adding model 'ConsolePort'
        db.create_table('device_consoleport', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('portId', self.gf('django.db.models.fields.IntegerField')()),
            ('parentDevice', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['device.Device'])),
        ))
        db.send_create_signal('device', ['ConsolePort'])

        # Adding model 'Link'
        db.create_table('device_link', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('switchPortA', self.gf('django.db.models.fields.related.ForeignKey')(related_name='linkA_set', to=orm['device.SwitchPort'])),
            ('switchPortB', self.gf('django.db.models.fields.related.ForeignKey')(related_name='linkB_set', to=orm['device.SwitchPort'])),
            ('comment', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('device', ['Link'])

        # Adding model 'PowerPort'
        db.create_table('device_powerport', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('socketId', self.gf('django.db.models.fields.IntegerField')()),
            ('parentDevice', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['device.Device'])),
        ))
        db.send_create_signal('device', ['PowerPort'])

        # Adding model 'DeviceClass'
        db.create_table('device_deviceclass', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('description', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('device', ['DeviceClass'])


    def backwards(self, orm):
        # Deleting model 'Vlan'
        db.delete_table('device_vlan')

        # Deleting model 'SwitchPort'
        db.delete_table('device_switchport')

        # Removing M2M table for field vlans on 'SwitchPort'
        db.delete_table('device_switchport_vlans')

        # Deleting model 'Device'
        db.delete_table('device_device')

        # Removing M2M table for field deviceClasses on 'Device'
        db.delete_table('device_device_deviceClasses')

        # Removing M2M table for field powerPorts on 'Device'
        db.delete_table('device_device_powerPorts')

        # Removing M2M table for field consolePorts on 'Device'
        db.delete_table('device_device_consolePorts')

        # Removing M2M table for field switchPorts on 'Device'
        db.delete_table('device_device_switchPorts')

        # Deleting model 'ConsolePort'
        db.delete_table('device_consoleport')

        # Deleting model 'Link'
        db.delete_table('device_link')

        # Deleting model 'PowerPort'
        db.delete_table('device_powerport')

        # Deleting model 'DeviceClass'
        db.delete_table('device_deviceclass')


    models = {
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
        'device.link': {
            'Meta': {'object_name': 'Link'},
            'comment': ('django.db.models.fields.TextField', [], {}),
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
            'vlans': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['device.Vlan']", 'symmetrical': 'False'})
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