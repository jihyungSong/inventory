import logging

from spaceone.core import utils
from spaceone.core.manager import BaseManager
from spaceone.inventory.model.device_template_model import DeviceTemplate
from spaceone.inventory.lib.resource_manager import ResourceManager


_LOGGER = logging.getLogger(__name__)


class DeviceTemplateManager(BaseManager, ResourceManager):

    resource_keys = ['device_template_id']
    query_method = 'list_device_templates'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.device_tpl_model: DeviceTemplate = self.locator.get_model('DeviceTemplate')

    def create_device_template(self, params):
        def _rollback(device_tpl_vo):
            _LOGGER.info(f'[ROLLBACK] Delete Device Template : {device_tpl_vo.name}')
            device_tpl_vo.delete(True)

        device_tpl_vo: DeviceTemplate = self.device_tpl_model.create(params)
        self.transaction.add_rollback(_rollback, device_tpl_vo)

        return device_tpl_vo

    def update_device_template(self, params):
        return self.update_device_template_by_vo(params, self.get_device_template(params['device_template_id'],
                                                                                  params['domain_id']))

    def update_device_template_by_vo(self, params, device_template_vo):
        def _rollback(old_data):
            _LOGGER.info(f'[ROLLBACK] Revert Data : {old_data.get("device_template_id")}')
            device_template_vo.update(old_data)

        self.transaction.add_rollback(_rollback, device_template_vo.to_dict())
        return device_template_vo.update(params)

    def delete_device_template(self, device_template_id, domain_id):
        self.delete_device_template_by_vo(self.get_device_template(device_template_id, domain_id))

    def get_device_template(self, device_template_id, domain_id, only=None):
        return self.device_tpl_model.get(device_template_id=device_template_id, domain_id=domain_id, only=only)

    def list_device_templates(self, query):
        device_template_vos, total_count = self.device_tpl_model.query(**query)
        return device_template_vos, total_count

    def stat_device_templates(self, query):
        return self.device_tpl_model.stat(**query)

    @staticmethod
    def delete_device_template_by_vo(cloud_svc_type_vo):
        cloud_svc_type_vo.delete()
