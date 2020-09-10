import jsonschema

from spaceone.core.service import *
from spaceone.inventory.manager.device_type_manager import DeviceTypeManager
from spaceone.inventory.error import *


@authentication_handler
@authorization_handler
@event_handler
class DeviceTypeService(BaseService):

    def __init__(self, metadata):
        super().__init__(metadata)
        self.device_type_mgr: DeviceTypeManager = self.locator.get_manager('DeviceTypeManager')

    @transaction
    @check_required(['name', 'domain_id'])
    def create(self, params):
        """
        Args:
            params (dict): {
                    'name': 'str',
                    'parent_device_type_id': 'str',
                    'template': 'dict',
                    'metadata': 'dict',
                    'labels': 'list,
                    'tags': 'dict',
                    'domain_id': 'str'
                }

        Returns:
            device_type_vo (object)
        """
        device_schema = params.get('template', {}).get('device', {}).get('schema', {})
        self._check_schema(device_schema)

        if 'parent_device_type_id' in params:
            parent_device_type_vo = self.device_type_mgr.get_device_type(params['parent_device_type_id'],
                                                                         params['domain_id'])

            parent_device_type_template = parent_device_type_vo.template
            parent_device_schema = parent_device_type_template.get('device', {}).get('schema', {})
            self._check_duplicate_schema_key(device_schema, parent_device_schema)

            params['parent_device_type'] = parent_device_type_vo
            del params['parent_device_type_id']

        return self.device_type_mgr.create_device_type(params)

    @transaction
    @check_required(['device_type_id', 'domain_id'])
    def update(self, params):
        """
        Args:
            params (dict): {
                    'device_type_id': 'str',
                    'template': 'dict',
                    'metadata': 'dict',
                    'force': 'bool',
                    'labels': 'list,
                    'tags': 'dict',
                    'domain_id': 'str'
                }

        Returns:
            device_type_vo (object)
        """

        device_type_vo = self.device_type_mgr.get_device_type(params['device_type_id'], params['domain_id'])

        update_params = {'domain_id': params['domain_id']}

        if params.get('force', False):
            # TODO
            pass

        if 'template' in params:
            update_schema = params.get('template', {}).get('device', {}).get('schema', {})
            self._check_schema(update_schema)

            old_device_type_template = device_type_vo.template
            old_schema = old_device_type_template.get('device', {}).get('schema', {})

            self._check_schema_data_type(old_schema, update_schema)

        if 'labels' in params:
            update_params['labels'] = params['labels']

        if 'tags' in params:
            update_params['tags'] = params['tags']

        return self.device_type_mgr.update_device_type_by_vo(params, device_type_vo)

    @transaction
    @check_required(['device_type_id', 'domain_id'])
    def delete(self, params):
        """
        Args:
            params (dict): {
                    'device_type_id': 'str',
                    'domain_id': 'str'
                }

        Returns:
            None

        """
        device_type_vo = self.device_type_mgr.get_device_type(params['device_type_id'], params['domain_id'])

        self.device_type_mgr.delete_device_type_by_vo(device_type_vo)

    @transaction
    @check_required(['device_type_id', 'domain_id'])
    def get(self, params):
        """
        Args:
            params (dict): {
                    'device_type_id': 'str',
                    'domain_id': 'str',
                    'only': 'list'
                }

        Returns:
            device_type_vo (object)
        """

        return self.device_type_mgr.get_device_type(params['device_type_id'], params['domain_id'], params.get('only'))

    @transaction
    @check_required(['domain_id'])
    @append_query_filter(['device_type_id', 'name', 'domain_id'])
    @append_keyword_filter(['device_type_id', 'name'])
    def list(self, params):
        """
        Args:
            params (dict): {
                    'device_type_id': 'str',
                    'name': 'str',
                    'domain_id': 'str',
                    'query': 'dict (spaceone.api.core.v1.Query)'
                }

        Returns:
            results (list)
            total_count (int)
        """

        return self.device_type_mgr.list_device_types(params.get('query', {}))

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
        return self.device_type_mgr.stat_device_types(query)

    @staticmethod
    def _check_schema(schema):
        try:
            jsonschema.Draft7Validator.check_schema(schema)
        except Exception as e:
            raise ERROR_INVALID_SCHEMA(key='schema')

    @staticmethod
    def _check_duplicate_schema_key(schema1, schema2):
        schema1_keys = [_key for _key in schema1.get('properties', {})]
        schema2_keys = [_key for _key in schema2.get('properties', {})]

        for schema1_key in schema1_keys:
            if schema1_key in schema2_keys:
                raise ERROR_DUPLICATE_DEVICE_TYPE_SCHEMA(key=schema1_key)

    @staticmethod
    def _check_schema_data_type(old_schema, new_schema):
        '''
        Check data type in JSON SCHEMA
        Can not modify data type in properties
        '''

        old_properties = old_schema.get('properties', {})
        new_properties = new_schema.get('properties', {})

        for key, property in new_properties.items():
            if key in old_properties and property.get('type', '') != old_properties[key].get('type', ''):
                raise ERROR_MODIFY_SCHEMA_TYPE(key=key, type=property.get('type'))
