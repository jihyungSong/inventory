import logging

from spaceone.core import utils
from spaceone.core.manager import BaseManager
from spaceone.inventory.model.device_type_model import DeviceType
from spaceone.inventory.lib.resource_manager import ResourceManager


_LOGGER = logging.getLogger(__name__)


class DeviceTypeManager(BaseManager, ResourceManager):

    resource_keys = ['device_type_id']
    query_method = 'list_device_types'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.device_type_model: DeviceType = self.locator.get_model('DeviceType')

    def create_device_type(self, params):
        def _rollback(device_type_vo):
            _LOGGER.info(f'[ROLLBACK] Delete Device Type : {device_type_vo.name}')
            device_type_vo.delete(True)

        device_type_vo: DeviceType = self.device_type_model.create(params)
        self.transaction.add_rollback(_rollback, device_type_vo)

        return device_type_vo

    def update_device_type(self, params):
        return self.update_device_type_by_vo(params,
                                             self.get_device_type(params['device_type_id'], params['domain_id']))

    def update_device_type_by_vo(self, params, device_type_vo):
        def _rollback(old_data):
            _LOGGER.info(f'[ROLLBACK] Revert Data : {old_data.get("device_type_id")}')
            device_type_vo.update(old_data)

        self.transaction.add_rollback(_rollback, device_type_vo.to_dict())
        return device_type_vo.update(params)

    def delete_device_type(self, device_type_id, domain_id):
        self.delete_device_type_by_vo(self.get_device_type(device_type_id, domain_id))

    def get_device_type(self, device_type_id, domain_id, only=None):
        return self.device_type_model.get(device_type_id=device_type_id, domain_id=domain_id, only=only)

    def list_device_types(self, query):
        device_type_vos, total_count = self.device_type_model.query(**query)
        return device_type_vos, total_count

    def stat_device_types(self, query):
        return self.device_type_model.stat(**query)

    @staticmethod
    def delete_device_type_by_vo(device_type_vo):
        device_type_vo.delete()
