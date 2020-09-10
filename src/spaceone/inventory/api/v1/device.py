from spaceone.api.inventory.v1 import device_pb2, device_pb2_grpc
from spaceone.core.pygrpc import BaseAPI


class Device(BaseAPI, device_pb2_grpc.DeviceServicer):

    pb2 = device_pb2
    pb2_grpc = device_pb2_grpc

    def create(self, request, context):
        params, metadata = self.parse_request(request, context)

        with self.locator.get_service('DeviceService', metadata) as device_service:
            return self.locator.get_info('DeviceInfo', device_service.create(params))

    def update(self, request, context):
        params, metadata = self.parse_request(request, context)

        with self.locator.get_service('DeviceService', metadata) as device_service:
            return self.locator.get_info('DeviceInfo', device_service.update(params))

    def pin_data(self, request, context):
        params, metadata = self.parse_request(request, context)

        with self.locator.get_service('DeviceService', metadata) as device_service:
            return self.locator.get_info('DeviceInfo', device_service.pin_data(params))

    def delete(self, request, context):
        params, metadata = self.parse_request(request, context)

        with self.locator.get_service('DeviceService', metadata) as device_service:
            device_service.delete(params)
            return self.locator.get_info('EmptyInfo')

    def get(self, request, context):
        params, metadata = self.parse_request(request, context)

        with self.locator.get_service('DeviceService', metadata) as device_service:
            return self.locator.get_info('DeviceInfo', device_service.get(params))

    def list(self, request, context):
        params, metadata = self.parse_request(request, context)

        with self.locator.get_service('DeviceService', metadata) as device_service:
            device_vos, total_count = device_service.list(params)
            return self.locator.get_info('DevicesInfo', device_vos, total_count, minimal=self.get_minimal(params))

    def stat(self, request, context):
        params, metadata = self.parse_request(request, context)

        with self.locator.get_service('DeviceService', metadata) as device_service:
            return self.locator.get_info('StatisticsInfo', device_service.stat(params))
