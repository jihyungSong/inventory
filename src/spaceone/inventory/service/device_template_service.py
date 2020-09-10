from spaceone.core.service import *
from spaceone.inventory.manager.device_template_manager import DeviceTemplateManager
from spaceone.inventory.error import *


@authentication_handler
@authorization_handler
@event_handler
class DeviceTemplateService(BaseService):

    def __init__(self, metadata):
        super().__init__(metadata)
        self.device_tpl_mgr: DeviceTemplateManager = self.locator.get_manager('DeviceTemplateManager')

    @transaction
    @check_required(['name', 'device_type_id', 'data', 'domain_id'])
    def create(self, params):
        """
        Args:
            params (dict): {
                    'name': 'str',
                    'device_type_id': 'str',
                    'data': 'dict',
                    'tags': 'dict',
                    'domain_id': 'str'
                }

        Returns:
            device_template_vo (object)

        """
        return self.device_tpl_mgr.create_device_template(params)

    @transaction
    @check_required(['device_template_id', 'domain_id'])
    def update(self, params):
        """
        Args:
            params (dict): {
                    'device_template_id': 'str',
                    'name': 'str',
                    'data': 'dict',
                    'tags': 'dict',
                    'domain_id': 'str'
                }

        Returns:
            device_template_vo (object)

        """
        device_tpl_vo = self.device_tpl_mgr.get_device_template(params['device_template_id'], params['domain_id'])
        return self.device_tpl_mgr.update_device_template_by_vo(params, device_tpl_vo)

    @transaction
    @check_required(['device_template_id', 'domain_id'])
    def delete(self, params):
        """
        Args:
            params (dict): {
                    'device_template_id': 'str',
                    'domain_id': 'str'
                }

        Returns:
            None

        """

        device_tpl_vo = self.device_tpl_mgr.get_device_template(params['device_template_id'], params['domain_id'])
        self.device_tpl_mgr.delete_device_template_by_vo(device_tpl_vo)

    @transaction
    @check_required(['device_template_id', 'domain_id'])
    def get(self, params):
        """
        Args:
            params (dict): {
                    'device_template_id': 'str',
                    'domain_id': 'str',
                    'only': 'list'
                }

        Returns:
            device_template_vo (object)

        """

        return self.device_tpl_mgr.get_device_template(params['device_template_id'], params['domain_id'],
                                                       params.get('only'))

    @transaction
    @check_required(['domain_id'])
    @append_query_filter(['device_template_id', 'name', 'device_type_id', 'domain_id'])
    @append_keyword_filter(['device_template_id', 'name', 'device_type_id'])
    def list(self, params):
        """
        Args:
            params (dict): {
                    'device_template_id': 'str',
                    'device_type_id': 'str',
                    'name': 'str',
                    'domain_id': 'str',
                    'query': 'dict (spaceone.api.core.v1.Query)'
                }

        Returns:
            results (list)
            total_count (int)

        """

        return self.device_tpl_mgr.list_device_templates(params.get('query', {}))

    @transaction
    @check_required(['query', 'domain_id'])
    @append_query_filter(['domain_id'])
    def stat(self, params):
        """
        Args:
            params (dict): {
                'domain_id': 'str',
                'query': 'dict (spaceone.api.core.v1.StatisticsQuery)'
            }

        Returns:
            values (list) : 'list of statistics data'

        """

        query = params.get('query', {})
        return self.device_tpl_mgr.stat_device_templates(query)
