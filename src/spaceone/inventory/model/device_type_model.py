from mongoengine import *

from spaceone.core.model.mongo_model import MongoModel


class DeviceType(MongoModel):
    device_type_id = StringField(max_length=40, generate_id='device-type', unique=True)
    name = StringField(max_length=255)
    parent_device_type = ReferenceField('self', null=True, default=None, reverse_delete_rule=DENY)
    labels = ListField(StringField(max_length=255))
    metadata = DictField()
    template = DictField()
    tags = DictField()
    domain_id = StringField(max_length=40)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)

    meta = {
        'updatable_fields': [
            'metadata',
            'template',
            'labels',
            'tags',
        ],
        'exact_fields': [
            'device_type_id',
            'domain_id',
        ],
        'minimal_fields': [
            'device_type_id',
            'name',
            'domain_id'
        ],
        'ordering': [
            'name',
        ],
        'indexes': [
            'device_type_id',
            'name',
            'domain_id',
        ]
    }
