from spaceone.api.inventory.v1 import device_type_pb2, device_type_pb2_grpc
from spaceone.core.pygrpc import BaseAPI


class DeviceType(BaseAPI, device_type_pb2_grpc.DeviceTypeServicer):

    pb2 = device_type_pb2
    pb2_grpc = device_type_pb2_grpc

    def create(self, request, context):
        params, metadata = self.parse_request(request, context)

        with self.locator.get_service('DeviceTypeService', metadata) as device_type_service:
            return self.locator.get_info('DeviceTypeInfo', device_type_service.create(params))

    def update(self, request, context):
        params, metadata = self.parse_request(request, context)

        with self.locator.get_service('DeviceTypeService', metadata) as device_type_service:
            return self.locator.get_info('DeviceTypeInfo', device_type_service.update(params))

    def delete(self, request, context):
        params, metadata = self.parse_request(request, context)

        with self.locator.get_service('DeviceTypeService', metadata) as device_type_service:
            device_type_service.delete(params)
            return self.locator.get_info('EmptyInfo')

    def get(self, request, context):
        params, metadata = self.parse_request(request, context)

        with self.locator.get_service('DeviceTypeService', metadata) as device_type_service:
            return self.locator.get_info('DeviceTypeInfo', device_type_service.get(params))

    def list(self, request, context):
        params, metadata = self.parse_request(request, context)

        with self.locator.get_service('DeviceTypeService', metadata) as device_type_service:
            device_type_vos, total_count = device_type_service.list(params)
            return self.locator.get_info('DeviceTypesInfo', device_type_vos, total_count,
                                         minimal=self.get_minimal(params))

    def stat(self, request, context):
        params, metadata = self.parse_request(request, context)

        with self.locator.get_service('DeviceTypeService', metadata) as device_type_service:
            return self.locator.get_info('StatisticsInfo', device_type_service.stat(params))
