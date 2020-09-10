from mongoengine import *

from spaceone.core.model.mongo_model import MongoModel
from spaceone.inventory.model.device_type_model import DeviceType


class DeviceTemplate(MongoModel):
    device_template_id = StringField(max_length=40, generate_id='device-tpl', unique=True)
    name = StringField(max_length=255)
    device_type = ReferenceField('DeviceType', reverse_delete_rule=DENY)
    data = DictField()
    tags = DictField()
    domain_id = StringField(max_length=40)
    created_at = DateTimeField(auto_now_add=True)

    meta = {
        'updatable_fields': [
            'name',
            'data',
            'tags',
        ],
        'exact_fields': [
            'device_template_id',
            'domain_id',
        ],
        'minimal_fields': [
            'device_template_id',
            'name',
            'domain_id'
        ],
        'ordering': [
            'name',
        ],
        'indexes': [
            'device_template_id',
            'name',
            'device_type',
            'domain_id',
        ]
    }
