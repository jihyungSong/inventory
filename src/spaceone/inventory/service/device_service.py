from spaceone.core.service import *
from spaceone.inventory.manager.device_manager import DeviceManager
from spaceone.inventory.manager.device_type_manager import DeviceTypeManager
from spaceone.inventory.manager.identity_manager import IdentityManager
from spaceone.inventory.manager.collection_data_manager import CollectionDataManager
from spaceone.inventory.error import *


@authentication_handler
@authorization_handler
@event_handler
class DeviceService(BaseService):

    def __init__(self, metadata):
        super().__init__(metadata)
        self.device_mgr: DeviceManager = self.locator.get_manager('DeviceManager')

    @transaction
    @check_required(['device_type_id', 'data', 'domain_id'])
    def create(self, params):
        """
        Args:
            params (dict): {
                    'device_type_id': 'str',
                    'data': 'dict',
                    'reference': 'dict',
                    'project_id': 'str',
                    'region_code': 'str,
                    'region_type': 'str,
                    'tags': 'dict',
                    'domain_id': 'str'
                }

        Returns:
            device_vo (object)

        """
        project_id = params.get('project_id')
        domain_id = params['domain_id']
        secret_project_id = self.transaction.get_meta('secret.project_id')

        device_type_mgr: DeviceTypeManager = self.locator.get_manager('DeviceTypeManager')
        identity_mgr: IdentityManager = self.locator.get_manager('IdentityManager')
        device_type_vo = device_type_mgr.get_device_type(params['device_type_id'], params['domain_id'])
        params['device_type'] = device_type_vo

        if project_id:
            # Validation Check
            identity_mgr.get_project(project_id, domain_id)
        elif secret_project_id:
            # SKIP Validation Check
            params['project_id'] = secret_project_id

        if 'region_code' in params and 'region_type' not in params:
            raise ERROR_REQUIRED_PARAMETER(key='region_type')

        if 'region_type' in params and 'region_code' not in params:
            raise ERROR_REQUIRED_PARAMETER(key='region_code')

        if 'region_code' in params and 'region_type' in params:
            # SKIP Validation Check
            params['region_ref'] = f'{params["region_type"]}.{params["region_code"]}'

        # TODO: Validation data with template
        data_mgr: CollectionDataManager = self.locator.get_manager('CollectionDataManager')
        params['collection_info'] = data_mgr.create_new_history(params, exclude_keys=['domain_id'])

        return self.device_mgr.create_device(params)

    @transaction
    @check_required(['device_id', 'domain_id'])
    def update(self, params):
        """
        Args:
            params (dict): {
                    'device_id': 'str',
                    'data': 'dict',
                    'reference': 'dict',
                    'release_project': 'bool',
                    'release_region': 'bool',
                    'project_id': 'str',
                    'region_code': 'str',
                    'region_type': 'str',
                    'tags': 'dict',
                    'domain_id': 'str'
                }

        Returns:
            device_vo (object)

        """
        project_id = params.get('project_id')
        secret_project_id = self.transaction.get_meta('secret.project_id')

        domain_id = params['domain_id']
        release_region = params.get('release_region', False)
        release_project = params.get('release_project', False)

        data_mgr: CollectionDataManager = self.locator.get_manager('CollectionDataManager')
        identity_mgr: IdentityManager = self.locator.get_manager('IdentityManager')

        device_vo = self.device_mgr.get_device(params['device_id'], domain_id)

        if release_region:
            params.update({
                'region_code': None,
                'region_type': None,
                'region_ref': None
            })
        else:
            if 'region_code' in params and 'region_type' not in params:
                raise ERROR_REQUIRED_PARAMETER(key='region_type')

            if 'region_type' in params and 'region_code' not in params:
                raise ERROR_REQUIRED_PARAMETER(key='region_code')

            if 'region_code' in params and 'region_type' in params:
                # SKIP Validation Check
                params['region_ref'] = f'{params["region_type"]}.{params["region_code"]}'

        if release_project:
            params['project_id'] = None
        elif project_id:
            # Validation Check
            identity_mgr.get_project(project_id, domain_id)
        elif secret_project_id:
            # SKIP Validation Check
            params['project_id'] = secret_project_id

        # TODO: Validation data with template

        exclude_keys = ['device_id', 'domain_id']
        params = data_mgr.merge_data_by_history(params, device_vo.to_dict(), exclude_keys=exclude_keys)

        return self.device_mgr.update_device_by_vo(params, device_vo)

    @transaction
    @check_required(['device_id', 'keys', 'domain_id'])
    def pin_data(self, params):
        """
        Args:
            params (dict): {
                    'device_id': 'str',
                    'keys': 'list',
                    'domain_id': 'str'
                }

        Returns:
            device_vo (object)

        """

        data_mgr: CollectionDataManager = self.locator.get_manager('CollectionDataManager')

        device_vo = self.device_mgr.get_device(params['device_id'], params['domain_id'])

        params['collection_info'] = data_mgr.update_pinned_keys(params['keys'], device_vo.collection_info.to_dict())

        return self.device_mgr.update_device_by_vo(params, device_vo)

    @transaction
    @check_required(['device_id', 'domain_id'])
    def delete(self, params):
        """
        Args:
            params (dict): {
                    'device_id': 'str',
                    'domain_id': 'str'
                }

        Returns:
            None

        """

        device_vo = self.device_mgr.get_device(params['device_id'], params['domain_id'])
        self.device_mgr.delete_device_by_vo(device_vo)

    @transaction
    @check_required(['device_id', 'domain_id'])
    def get(self, params):
        """
        Args:
            params (dict): {
                    'device_id': 'str',
                    'domain_id': 'str',
                    'only': 'list'
                }

        Returns:
            device_vo (object)

        """

        return self.device_mgr.get_device(params['device_id'], params['domain_id'], params.get('only'))

    @transaction
    @check_required(['domain_id'])
    @append_query_filter(['device_id', 'device_type_id', 'project_id', 'region_code', 'region_type', 'domain_id'])
    @append_keyword_filter(['device_id', 'device_type_id', 'project_id', 'reference.resource_id'])
    def list(self, params):
        """
        Args:
            params (dict): {
                    'device_id': 'str',
                    'device_type_id': 'str',
                    'project_id': 'str',
                    'region_code': 'str',
                    'region_type': 'str',
                    'domain_id': 'str',
                    'query': 'dict (spaceone.api.core.v1.Query)'
                }

        Returns:
            results (list)
            total_count (int)

        """

        return self.device_mgr.list_devices(params.get('query', {}))

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
        return self.device_mgr.stat_devices(query)
