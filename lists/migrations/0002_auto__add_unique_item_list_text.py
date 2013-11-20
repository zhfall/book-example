# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding unique constraint on 'Item', fields ['list', 'text']
        db.create_unique('lists_item', ['list_id', 'text'])


    def backwards(self, orm):
        # Removing unique constraint on 'Item', fields ['list', 'text']
        db.delete_unique('lists_item', ['list_id', 'text'])


    models = {
        'lists.item': {
            'Meta': {'ordering': "('id',)", 'unique_together': "(('list', 'text'),)", 'object_name': 'Item'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'list': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['lists.List']"}),
            'text': ('django.db.models.fields.TextField', [], {})
        },
        'lists.list': {
            'Meta': {'object_name': 'List'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        }
    }

    complete_apps = ['lists']