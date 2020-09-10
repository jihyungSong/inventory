import functools
from spaceone.api.inventory.v1 import device_template_pb2
from spaceone.core.pygrpc.message_type import *
from spaceone.inventory.model.device_template_model import DeviceTemplate

__all__ = ['DeviceTemplateInfo', 'DeviceTemplatesInfo']


def DeviceTemplateInfo(device_template_vo: DeviceTemplate, minimal=False):
    info = {
        'device_template_id': device_template_vo.device_template_id,
        'name': device_template_vo.name,
    }

    if not minimal:
        info.update({
            'data': change_struct_type(device_template_vo.data),
            'tags': change_struct_type(device_template_vo.tags),
            'domain_id': device_template_vo.domain_id,
            'created_at': change_timestamp_type(device_template_vo.created_at)
        })

    return device_template_pb2.DeviceTemplateInfo(**info)


def DeviceTemplatesInfo(device_template_vos, total_count, **kwargs):
    return device_template_pb2.DeviceTemplatesInfo(results=list(map(functools.partial(DeviceTemplateInfo, **kwargs),
                                                                    device_template_vos)),
                                                   total_count=total_count)
