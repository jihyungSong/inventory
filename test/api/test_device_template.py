import os
import uuid
import unittest
import pprint
from spaceone.core import utils, pygrpc
from spaceone.core.unittest.runner import RichTestRunner
from google.protobuf.json_format import MessageToDict


def random_string():
    return uuid.uuid4().hex


class TestDeviceTemplate(unittest.TestCase):
    config = utils.load_yaml_from_file(
        os.environ.get('SPACEONE_TEST_CONFIG_FILE', './config.yml'))

    pp = pprint.PrettyPrinter(indent=4)
    identity_v1 = None
    inventory_v1 = None
    domain = None
    domain_owner = None
    owner_id = None
    owner_pw = None
    token = None

    @classmethod
    def setUpClass(cls):
        super(TestDeviceTemplate, cls).setUpClass()
        endpoints = cls.config.get('ENDPOINTS', {})
        cls.identity_v1 = pygrpc.client(endpoint=endpoints.get('identity', {}).get('v1'), version='v1')
        cls.inventory_v1 = pygrpc.client(endpoint=endpoints.get('inventory', {}).get('v1'), version='v1')

        cls._create_domain()
        cls._create_domain_owner()
        cls._issue_owner_token()

    @classmethod
    def tearDownClass(cls):
        super(TestDeviceTemplate, cls).tearDownClass()
        cls.identity_v1.DomainOwner.delete({
            'domain_id': cls.domain.domain_id,
            'owner_id': cls.owner_id
        })

        if cls.domain:
            cls.identity_v1.Domain.delete({'domain_id': cls.domain.domain_id})

    @classmethod
    def _create_domain(cls):
        name = utils.random_string()
        param = {
            'name': name,
            'tags': {utils.random_string(): utils.random_string(), utils.random_string(): utils.random_string()},
            'config': {
                'aaa': 'bbbb'
            }
        }

        cls.domain = cls.identity_v1.Domain.create(param)
        print(f'domain_id: {cls.domain.domain_id}')
        print(f'domain_name: {cls.domain.name}')

    @classmethod
    def _create_domain_owner(cls):
        cls.owner_id = utils.random_string()[0:10]
        cls.owner_pw = 'qwerty'

        param = {
            'owner_id': cls.owner_id,
            'password': cls.owner_pw,
            'name': 'Steven' + utils.random_string()[0:5],
            'timezone': 'utc+9',
            'email': 'Steven' + utils.random_string()[0:5] + '@mz.co.kr',
            'mobile': '+821026671234',
            'domain_id': cls.domain.domain_id
        }

        owner = cls.identity_v1.DomainOwner.create(
            param
        )
        cls.domain_owner = owner
        print(f'owner_id: {cls.owner_id}')
        print(f'owner_pw: {cls.owner_pw}')

    @classmethod
    def _issue_owner_token(cls):
        token_param = {
            'credentials': {
                'user_type': 'DOMAIN_OWNER',
                'user_id': cls.owner_id,
                'password': cls.owner_pw
            },
            'domain_id': cls.domain.domain_id
        }

        issue_token = cls.identity_v1.Token.issue(token_param)
        cls.token = issue_token.access_token
        print(f'token: {cls.token}')

    def _print_data(self, message, description=None):
        print()
        if description:
            print(f'[ {description} ]')

        self.pp.pprint(MessageToDict(message, preserving_proto_field_name=True))

    def setUp(self):
        self.device_type = None
        self.device_types = []
        self.device_template = None
        self.device_templates = []

    def tearDown(self):
        for device_template in self.device_templates:
            self.inventory_v1.DeviceTemplate.delete(
                {'device_template_id': device_template.device_template_id,
                 'domain_id': self.domain.domain_id},
                metadata=(('token', self.token),)
            )

        for device_type in self.device_types:
            self.inventory_v1.DeviceType.delete(
                {'device_type_id': device_type.device_type_id,
                 'domain_id': self.domain.domain_id},
                metadata=(('token', self.token),)
            )

    def test_create_device_template(self, name=None, device_type_id=None):
        """ Create Device Template
        """

        if name is None:
            name = random_string()

        params = {
            'name': name,
            'data': {
                'aaa': 'bbb',
                'xxx': {
                    'yyy': 'zzzz'
                }
            },
            'tags': {
                'description': 'test'
            },
            'domain_id': self.domain.domain_id
        }

        if device_type_id:
            params.update({
                'device_type_id': device_type_id
            })
        else:
            self.test_create_device_type()
            params.update({
                'device_type_id': self.device_type.device_type_id
            })

        self.device_template = self.inventory_v1.DeviceTemplate.create(
            params, metadata=(('token', self.token),)
        )

        self._print_data(self.device_type, 'test_create_device_type')

        self.device_templates.append(self.device_template)
        self.assertEqual(self.device_template.name, name)

    def test_create_device_type(self, name=None, parent_device_type_id=None):
        """ Create Device Type
        """

        if name is None:
            name = random_string()

        params = {
            'name': name,
            'template': {
                'device': {
                    'schema': {}
                }
            },
            'metadata': {
                'view': {
                    'search': [{
                        'name': 'Name',
                        'key': 'name'
                    }, {
                        'name': 'Project',
                        'key': 'project'
                    }]
                }
            },
            'labels': ['abc', 'def', 'ghi'],
            'tags': {
                'description': 'test'
            },
            'domain_id': self.domain.domain_id
        }

        if parent_device_type_id:
            params.update({
                'parent_device_type_id': parent_device_type_id
            })

        self.device_type = self.inventory_v1.DeviceType.create(
            params, metadata=(('token', self.token),)
        )

        self._print_data(self.device_type, 'test_create_device_type')
        self.device_types.append(self.device_type)

    def test_update_device_template_data(self):
        self.test_create_device_template()

        data = {
            'changed': 'ok'
        }

        param = {
            'device_template_id': self.device_template.device_template_id,
            'data': data,
            'domain_id': self.domain.domain_id,
        }
        self.device_template = self.inventory_v1.DeviceTemplate.update(
            param,
            metadata=(('token', self.token),)
        )

        self._print_data(self.device_template, 'test_update_device_template_data')

    def test_update_device_template_name(self):
        self.test_create_device_template()

        name = 'device-template-test'

        param = {
            'device_template_id': self.device_template.device_template_id,
            'name': name,
            'domain_id': self.domain.domain_id,
        }
        self.device_template = self.inventory_v1.DeviceTemplate.update(
            param,
            metadata=(('token', self.token),)
        )

        self._print_data(self.device_template, 'test_update_device_template_data')

    def test_update_device_template_tags(self):
        self.test_create_device_template()

        tags = {
            random_string(): random_string(),
            random_string(): random_string()
        }
        param = {
            'device_template_id': self.device_template.device_template_id,
            'tags': tags,
            'domain_id': self.domain.domain_id,
        }

        self.device_template = self.inventory_v1.DeviceTemplate.update(param, metadata=(('token', self.token),))
        self.assertEqual(MessageToDict(self.device_template.tags), tags)

    def test_get_device_template(self):
        name = 'test-device-type'
        self.test_create_device_template(name=name)

        param = {
            'device_template_id': self.device_template.device_template_id,
            'domain_id': self.domain.domain_id
        }
        self.device_template = self.inventory_v1.DeviceTemplate.get(param, metadata=(('token', self.token),))
        self.assertEqual(self.device_template.name, name)

    def test_list_device_templates(self):
        self.test_create_device_template()
        self.test_create_device_template()
        self.test_create_device_template()

        param = {
            'device_template_id': self.device_template.device_template_id,
            'domain_id': self.domain.domain_id
        }

        device_templates = self.inventory_v1.DeviceTemplate.list(param, metadata=(('token', self.token),))

        self.assertEqual(1, device_templates.total_count)

    def test_list_device_templates_name(self):
        name = random_string()

        self.test_create_device_template(name=name)
        self.test_create_device_template(name=name)
        self.test_create_device_template(name=name)
        self.test_create_device_template()
        self.test_create_device_template()
        self.test_create_device_template()

        param = {
            'name': name,
            'domain_id': self.domain.domain_id
        }

        device_templates = self.inventory_v1.DeviceTemplate.list(param, metadata=(('token', self.token),))

        self.assertEqual(3, device_templates.total_count)

    def test_list_query(self):
        self.test_create_device_template()
        self.test_create_device_template()
        self.test_create_device_template()
        self.test_create_device_template()
        self.test_create_device_template()
        self.test_create_device_template()

        param = {
            'domain_id': self.domain.domain_id,
            'query': {
                'filter': [
                    {
                        'k': 'device_template_id',
                        'v': list(map(lambda device_template: device_template.device_template_id, self.device_templates)),
                        'o': 'in'
                    }
                ]
            }
        }

        device_templates = self.inventory_v1.DeviceTemplate.list(param, metadata=(('token', self.token),))

        print(device_templates)
        self.assertEqual(len(self.device_templates), device_templates.total_count)

    def test_stat_device_template(self):
        self.test_list_query()

        params = {
            'domain_id': self.domain.domain_id,
            'query': {
                'aggregate': {
                    'group': {
                        'keys': [{
                            'key': 'device_template_id',
                            'name': 'Id'
                        }],
                        'fields': [{
                            'operator': 'count',
                            'name': 'Count'
                        }]
                    }
                },
                'sort': {
                    'name': 'Id',
                    'desc': True
                }
            }
        }

        result = self.inventory_v1.DeviceTemplate.stat(
            params, metadata=(('token', self.token),))

        self._print_data(result, 'test_stat_device_template')


if __name__ == "__main__":
    unittest.main(testRunner=RichTestRunner)

