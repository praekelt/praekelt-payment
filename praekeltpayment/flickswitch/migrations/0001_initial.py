# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'FlickSwitchPayment'
        db.create_table('flickswitch_flickswitchpayment', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('msisdn', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('amount', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('fail_reason', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('fail_code', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('state', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
        ))
        db.send_create_signal('flickswitch', ['FlickSwitchPayment'])


    def backwards(self, orm):
        # Deleting model 'FlickSwitchPayment'
        db.delete_table('flickswitch_flickswitchpayment')


    models = {
        'flickswitch.flickswitchpayment': {
            'Meta': {'object_name': 'FlickSwitchPayment'},
            'amount': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'fail_code': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'fail_reason': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'msisdn': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'state': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'})
        }
    }

    complete_apps = ['flickswitch']