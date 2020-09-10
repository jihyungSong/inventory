import os
import uuid
import unittest
import pprint
from spaceone.core import utils, pygrpc
from spaceone.core.unittest.runner import RichTestRunner
from google.protobuf.json_format import MessageToDict


def random_string():
    return uuid.uuid4().hex


class TestDeviceType(unittest.TestCase):
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
        super(TestDeviceType, cls).setUpClass()
        endpoints = cls.config.get('ENDPOINTS', {})
        cls.identity_v1 = pygrpc.client(endpoint=endpoints.get('identity', {}).get('v1'), version='v1')
        cls.inventory_v1 = pygrpc.client(endpoint=endpoints.get('inventory', {}).get('v1'), version='v1')

        cls._create_domain()
        cls._create_domain_owner()
        cls._issue_owner_token()

    @classmethod
    def tearDownClass(cls):
        super(TestDeviceType, cls).tearDownClass()
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

    def setUp(self):
        self.device_type = None
        self.device_types = []

    def tearDown(self):
        for device_type in self.device_types:
            self.inventory_v1.DeviceType.delete(
                {'device_type_id': device_type.device_type_id,
                 'domain_id': self.domain.domain_id},
                metadata=(('token', self.token),)
            )

    def _print_data(self, message, description=None):
        print()
        if description:
            print(f'[ {description} ]')

        self.pp.pprint(MessageToDict(message, preserving_proto_field_name=True))

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
        self.assertEqual(self.device_type.name, name)

    def test_create_device_type_with_parent_device_type(self):
        """ Create Cloud Service Type with data source
        """

        self.test_create_device_type()

        parent_device_type = self.device_type

        params = {
            'name': random_string(),
            'parent_device_type_id': parent_device_type.device_type_id,
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

        self.device_type = self.inventory_v1.DeviceType.create(params, metadata=(('token', self.token),))
        self._print_data(self.device_type, 'test_create_device_type_with_parent')

        self.assertEqual(self.device_type.parent_device_type_info.device_type_id, parent_device_type.device_type_id)

        self.inventory_v1.DeviceType.delete(
            {'device_type_id': self.device_type.device_type_id,
             'domain_id': self.domain.domain_id},
            metadata=(('token', self.token),)
        )

    def test_update_device_type_metadata(self):
        self.test_create_device_type()

        param = {
            'device_type_id': self.device_type.device_type_id,
            'metadata': {
                'view': {
                    'search': [{
                        'name': 'ABC',
                        'key': 'xxx'
                    }, {
                        'name': 'YYY',
                        'key': 'bbb'
                    }]
                }
            },
            'domain_id': self.domain.domain_id,
        }
        self.device_type = self.inventory_v1.DeviceType.update(
            param,
            metadata=(('token', self.token),)
        )

        self._print_data(self.device_type, 'test_update_device_type_metadata')

    def test_update_device_type_template(self):
        self.test_create_device_type()

        param = {
            'device_type_id': self.device_type.device_type_id,
            'labels': ['aa', 'bb'],
            'template': {
                'device': {
                    'schema': {
                        'test': 'ABCDE'
                    }
                }
            },
            'domain_id': self.domain.domain_id,
        }
        self.device_type = self.inventory_v1.DeviceType.update(
            param,
            metadata=(('token', self.token),)
        )

        self._print_data(self.device_type, 'test_update_device_type_metadata')

    def test_update_device_type_label(self):
        self.test_create_device_type()

        labels = [random_string(), random_string(), random_string()]

        param = {
            'device_type_id': self.device_type.device_type_id,
            'labels': labels,
            'domain_id': self.domain.domain_id,
        }

        self.device_type = self.inventory_v1.DeviceType.update(param, metadata=(('token', self.token),))

        for _label in self.device_type.labels:
            self.assertEqual(_label, labels[0])
            break

    def test_update_device_type_tags(self):
        self.test_create_device_type()

        tags = {
            random_string(): random_string(),
            random_string(): random_string()
        }
        param = {
            'device_type_id': self.device_type.device_type_id,
            'tags': tags,
            'domain_id': self.domain.domain_id,
        }

        self.device_type = self.inventory_v1.DeviceType.update(param, metadata=(('token', self.token),))
        self.assertEqual(MessageToDict(self.device_type.tags), tags)

    def test_get_device_type(self):
        name = 'test-device-type'
        self.test_create_device_type(name=name)

        param = {
            'device_type_id': self.device_type.device_type_id,
            'domain_id': self.domain.domain_id
        }
        self.device_type = self.inventory_v1.DeviceType.get(param, metadata=(('token', self.token),))
        self.assertEqual(self.device_type.name, name)

    def test_list_device_types(self):
        self.test_create_device_type()
        self.test_create_device_type()
        self.test_create_device_type()

        param = {
            'device_type_id': self.device_type.device_type_id,
            'domain_id': self.domain.domain_id
        }

        device_types = self.inventory_v1.DeviceType.list(param, metadata=(('token', self.token),))

        self.assertEqual(1, device_types.total_count)

    def test_list_device_types_name(self):
        self.test_create_device_type()
        self.test_create_device_type()
        self.test_create_device_type()
        self.test_create_device_type()
        self.test_create_device_type()
        self.test_create_device_type()

        param = {
            'name': self.device_type.name,
            'domain_id': self.domain.domain_id
        }

        device_types = self.inventory_v1.DeviceType.list(param, metadata=(('token', self.token),))

        self.assertEqual(1, device_types.total_count)

    def test_list_device_types_name(self):
        name = random_string()

        self.test_create_device_type(name=name)
        self.test_create_device_type(name=name)
        self.test_create_device_type(name=name)
        self.test_create_device_type()
        self.test_create_device_type()
        self.test_create_device_type()

        param = {
            'name': name,
            'domain_id': self.domain.domain_id
        }

        device_types = self.inventory_v1.DeviceType.list(param, metadata=(('token', self.token),))

        self.assertEqual(3, device_types.total_count)

    def test_list_query(self):
        self.test_create_device_type()
        self.test_create_device_type()
        self.test_create_device_type()
        self.test_create_device_type()
        self.test_create_device_type()
        self.test_create_device_type()

        param = {
            'domain_id': self.domain.domain_id,
            'query': {
                'filter': [
                    {
                        'k': 'device_type_id',
                        'v': list(map(lambda device_type: device_type.device_type_id, self.device_types)),
                        'o': 'in'
                    }
                ]
            }
        }

        device_types = self.inventory_v1.DeviceType.list(param, metadata=(('token', self.token),))

        print(device_types)
        self.assertEqual(len(self.device_types), device_types.total_count)

    def test_stat_device_type(self):
        self.test_list_query()

        params = {
            'domain_id': self.domain.domain_id,
            'query': {
                'aggregate': {
                    'group': {
                        'keys': [{
                            'key': 'device_type_id',
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

        result = self.inventory_v1.DeviceType.stat(
            params, metadata=(('token', self.token),))

        self._print_data(result, 'test_stat_device_type')


if __name__ == "__main__":
    unittest.main(testRunner=RichTestRunner)

