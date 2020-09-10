import functools
from spaceone.api.inventory.v1 import device_type_pb2
from spaceone.core.pygrpc.message_type import *
from spaceone.inventory.model.device_type_model import DeviceType

__all__ = ['DeviceTypeInfo', 'DeviceTypesInfo']


def DeviceTypeInfo(device_type_vo: DeviceType, minimal=False):
    info = {
        'device_type_id': device_type_vo.device_type_id,
        'name': device_type_vo.name,
    }

    if not minimal:
        info.update({
            'template': change_struct_type(device_type_vo.template),
            'metadata': change_struct_type(device_type_vo.metadata),
            'labels': change_list_value_type(device_type_vo.labels),
            'domain_id': device_type_vo.domain_id,
            'tags': change_struct_type(device_type_vo.tags),
            'created_at': change_timestamp_type(device_type_vo.created_at)
        })

        if device_type_vo.parent_device_type:
            info.update({
                'parent_device_type_info': DeviceTypeInfo(device_type_vo.parent_device_type, minimal=True)
            })

    return device_type_pb2.DeviceTypeInfo(**info)


def DeviceTypesInfo(device_type_vos, total_count, **kwargs):
    return device_type_pb2.DeviceTypesInfo(results=list(map(functools.partial(DeviceTypeInfo, **kwargs),
                                                            device_type_vos)),
                                           total_count=total_count)
