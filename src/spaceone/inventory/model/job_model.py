from mongoengine import *

from spaceone.core.model.mongo_model import MongoModel
from spaceone.inventory.model.collector_model import Collector

class Error(EmbeddedDocument):
    error_code = StringField(max_length=128)
    message = StringField(max_length=2048)
    additional = DictField()


class Job(MongoModel):
    job_id = StringField(max_length=40, generate_id='job', unique=True)
    status = StringField(max_length=20, default='CREATED',
                choices=('CREATED', 'CANCELED', 'IN_PROGRESS', 'SUCCESS', 'ERROR', 'TIMEOUT'))
    filters = DictField()
    total_tasks = IntField(min_value=0, max_value=65000, default=0)
    remained_tasks = IntField(max_value=65000, default=0)          # Number of remained from collector, 0 means No remained_task
    errors = ListField(EmbeddedDocumentField(Error, default=None, null=True))
    collector = ReferenceField('Collector', reverse_delete_rule=NULLIFY)
    project_id = StringField(max_length=255, default=None, null=True)
    domain_id = StringField(max_length=255)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)
    finished_at = DateTimeField(default=None, null=True)
    mark_error = IntField(min_value=0, default=0)

    meta = {
        'updatable_fields': [
            'status',
            'total_tasks',
            'remained_tasks',
            'errors',
            'finished_at',
            'mark_error',
        ],
        'exact_fields': [
            'job_id',
            'status',
            'project_id',
            'domain_id',
        ],
        'minimal_fields': [
            'job_id',
            'status',
            'created_at',
            'finished_at',
        ],
        'change_query_keys': {
            'collector_id': 'collector.collector_id'
        },
        'reference_query_keys': {
            'collector': Collector
        },
        'ordering': [
            '-created_at'
        ],
        'indexes': [
            'job_id',
            'status',
            'collector',
            'project_id',
            'domain_id',
        ],
        'aggregate': {
            'lookup': {
                'collector': {
                    'from': 'collector'
                }
            }
        }
    }

