from mongoengine import *
from spaceone.core.model.mongo_model import MongoModel


class Resource(EmbeddedDocument):
    resource_type = StringField()
    filter = ListField(DictField())


class ResourceGroup(MongoModel):
    resource_group_id = StringField(max_length=40, generate_id='rsc-grp', unique=True)
    name = StringField(max_length=255)
    resources = ListField(EmbeddedDocumentField(Resource))
    tags = DictField()
    project_id = StringField(max_length=255)
    domain_id = StringField(max_length=255)
    created_at = DateTimeField(auto_now_add=True)

    meta = {
        'updatable_fields': [
            'name',
            'resources',
            'project_id',
            'tags'
        ],
        'exact_fields': [
            'resource_group_id',
            'project_id',
            'domain_id'
        ],
        'minimal_fields': [
            'resource_group_id',
            'name',
            'project_id'
        ],
        'change_query_keys': {},
        'ordering': [
            'name'
        ],
        'indexes': [
            'resource_group_id',
            'project_id',
            'domain_id',
        ]
    }
