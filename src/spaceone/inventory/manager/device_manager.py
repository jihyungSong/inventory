import logging

from spaceone.core import utils
from spaceone.core.manager import BaseManager
from spaceone.inventory.model.device_model import Device
from spaceone.inventory.lib.resource_manager import ResourceManager


_LOGGER = logging.getLogger(__name__)


class DeviceManager(BaseManager, ResourceManager):

    resource_keys = ['device_id']
    query_method = 'list_devices'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.device_model: Device = self.locator.get_model('Device')

    def create_device(self, params):
        def _rollback(device_vo):
            _LOGGER.info(f'[ROLLBACK] Delete Device : {device_vo.device_id}')
            device_vo.delete()

        device_vo: Device = self.device_model.create(params)
        self.transaction.add_rollback(_rollback, device_vo)

        return device_vo

    def update_device(self, params):
        return self.update_device_by_vo(params, self.get_device(params['device_id'], params['domain_id']))

    def update_device_by_vo(self, params, device_vo):
        def _rollback(old_data):
            _LOGGER.info(f'[ROLLBACK] Revert Data : {old_data.get("device_id")}')
            device_vo.update(old_data)

        self.transaction.add_rollback(_rollback, device_vo.to_dict())
        return device_vo.update(params)

    def delete_device(self, device_id, domain_id):
        self.delete_device_by_vo(self.get_device(device_id, domain_id))

    def get_device(self, device_id, domain_id, only=None):
        return self.device_model.get(device_id=device_id, domain_id=domain_id, only=only)

    def list_devices(self, query):
        device_vos, total_count = self.device_model.query(**query)
        return device_vos, total_count

    def stat_devices(self, query):
        return self.device_model.stat(**query)

    @staticmethod
    def delete_device_by_vo(cloud_svc_type_vo):
        cloud_svc_type_vo.delete()
