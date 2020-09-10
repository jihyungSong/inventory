from mongoengine import *

from spaceone.core.model.mongo_model import MongoModel
from spaceone.inventory.model.device_type_model import DeviceType
from spaceone.inventory.model.collection_info_model import CollectionInfo
from spaceone.inventory.model.reference_resource_model import ReferenceResource


class Device(MongoModel):
    device_id = StringField(max_length=40, generate_id='device', unique=True)
    state = StringField(max_length=255, default='INSERVICE', choices=('INSTOCK', 'INSERVICE', 'DELETED'))
    name = StringField(max_length=255)
    device_type = ReferenceField('DeviceType', reverse_delete_rule=CASCADE)
    region_code = StringField(max_length=255)
    region_type = StringField(max_length=255, choices=('AWS', 'GOOGLE_CLOUD', 'AZURE', 'DATACENTER'))
    region_ref = StringField(max_length=255)
    project_id = StringField(null=True, default=None, max_length=255)
    data = DictField()
    reference = EmbeddedDocumentField(ReferenceResource, default=ReferenceResource)
    tags = DictField()
    domain_id = StringField(max_length=40)
    collection_info = EmbeddedDocumentField(CollectionInfo, default=CollectionInfo)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)

    meta = {
        'updatable_fields': [
            'data',
            'state',
            'reference',
            'project_id',
            'region_code',
            'region_type',
            'tags',
        ],
        'exact_fields': [
            'device_id',
            'state',
            'device_type',
            'region_code',
            'region_type',
            'project_id',
            'reference.resource_id',
            'domain_id',
            'collection_info.state'
        ],
        'minimal_fields': [
            'device_id',
            'state',
            'name',
            'reference.resource_id',
            'domain_id'
        ],
        'ordering': [
            'name',
        ],
        'change_query_keys': {
            'device_type_id': 'device_type.device_type_id',
        },
        'reference_query_keys': {
            'device_type': DeviceType,
        },
        'indexes': [
            'device_id',
            'state',
            'name',
            'device_type',
            'region_code',
            'region_type',
            'project_id',
            'domain_id',
            'collection_info.state',
            'reference.resource_id',
        ]
    }
