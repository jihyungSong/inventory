import functools
from spaceone.api.inventory.v1 import device_pb2
from spaceone.core.pygrpc.message_type import *
from spaceone.inventory.model.device_model import Device
from spaceone.inventory.info.device_type_info import DeviceTypeInfo
from spaceone.inventory.info.collection_info import CollectionInfo

__all__ = ['DeviceInfo', 'DevicesInfo']


def DeviceInfo(device_vo: Device, minimal=False):
    info = {
        'device_id': device_vo.device_id,
        'state': device_vo.state,
        'project_id': device_vo.project_id,
        'reference': device_pb2.DeviceReference(
            **device_vo.reference.to_dict()) if device_vo.reference else None,
    }

    if not minimal:
        info.update({
            'data': change_struct_type(device_vo.data),
            'region_code': device_vo.region_code,
            'region_type': device_vo.region_type,
            'domain_id': device_vo.domain_id,
            'tags': change_struct_type(device_vo.tags),
            'device_type_info': DeviceTypeInfo(device_vo.device_type, minimal=True),
            'collection_info': CollectionInfo(device_vo.collection_info.to_dict()),
            'created_at': change_timestamp_type(device_vo.created_at),
            'updated_at': change_timestamp_type(device_vo.updated_at),
        })

    return device_pb2.DeviceInfo(**info)


def DevicesInfo(device_vos, total_count, **kwargs):
    return device_pb2.DevicesInfo(results=list(map(functools.partial(DeviceInfo, **kwargs), device_vos)),
                                  total_count=total_count)
