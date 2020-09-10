from spaceone.api.inventory.v1 import device_template_pb2, device_template_pb2_grpc
from spaceone.core.pygrpc import BaseAPI


class DeviceTemplate(BaseAPI, device_template_pb2_grpc.DeviceTemplateServicer):

    pb2 = device_template_pb2
    pb2_grpc = device_template_pb2_grpc

    def create(self, request, context):
        params, metadata = self.parse_request(request, context)

        with self.locator.get_service('DeviceTemplateService', metadata) as device_tpl_service:
            return self.locator.get_info('DeviceTemplateInfo', device_tpl_service.create(params))

    def update(self, request, context):
        params, metadata = self.parse_request(request, context)

        with self.locator.get_service('DeviceTemplateService', metadata) as device_tpl_service:
            return self.locator.get_info('DeviceTemplateInfo', device_tpl_service.update(params))

    def delete(self, request, context):
        params, metadata = self.parse_request(request, context)

        with self.locator.get_service('DeviceTemplateService', metadata) as device_tpl_service:
            device_tpl_service.delete(params)
            return self.locator.get_info('EmptyInfo')

    def get(self, request, context):
        params, metadata = self.parse_request(request, context)

        with self.locator.get_service('DeviceTemplateService', metadata) as device_tpl_service:
            return self.locator.get_info('DeviceTemplateInfo', device_tpl_service.get(params))

    def list(self, request, context):
        params, metadata = self.parse_request(request, context)

        with self.locator.get_service('DeviceTemplateService', metadata) as device_tpl_service:
            device_tpl_vos, total_count = device_tpl_service.list(params)
            return self.locator.get_info('DeviceTemplatesInfo', device_tpl_vos, total_count,
                                         minimal=self.get_minimal(params))

    def stat(self, request, context):
        params, metadata = self.parse_request(request, context)

        with self.locator.get_service('DeviceTemplateService', metadata) as device_tpl_service:
            return self.locator.get_info('StatisticsInfo', device_tpl_service.stat(params))
