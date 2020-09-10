import os
import uuid
import unittest
import pprint
from spaceone.core import utils, pygrpc
from spaceone.core.unittest.runner import RichTestRunner
from google.protobuf.json_format import MessageToDict


def random_string():
    return uuid.uuid4().hex


class TestDevice(unittest.TestCase):
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
        super(TestDevice, cls).setUpClass()
        endpoints = cls.config.get('ENDPOINTS', {})
        cls.identity_v1 = pygrpc.client(endpoint=endpoints.get('identity', {}).get('v1'), version='v1')
        cls.inventory_v1 = pygrpc.client(endpoint=endpoints.get('inventory', {}).get('v1'), version='v1')

        cls._create_domain()
        cls._create_domain_owner()
        cls._issue_owner_token()

    @classmethod
    def tearDownClass(cls):
        super(TestDevice, cls).tearDownClass()
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
        self.device = None
        self.devices = []
        self.regions = []
        self.region = None
        self.projects = []
        self.project = None
        self.project_groups = []
        self.project_group = None

    def tearDown(self):
        for device_type in self.device_types:
            self.inventory_v1.DeviceType.delete(
                {'device_type_id': device_type.device_type_id,
                 'domain_id': self.domain.domain_id},
                metadata=(('token', self.token),)
            )

        for region in self.regions:
            self.inventory_v1.Region.delete(
                {'region_id': region.region_id,
                 'domain_id': self.domain.domain_id},
                metadata=(('token', self.token),)
            )
            print(f'>> delete region: {region.name} ({region.region_id})')

        for project in self.projects:
            self.identity_v1.Project.delete(
                {'project_id': project.project_id,
                 'domain_id': self.domain.domain_id},
                metadata=(('token', self.token),)
            )
            print(f'>> delete project: {project.name} ({project.project_id})')

        for project_group in self.project_groups:
            self.identity_v1.ProjectGroup.delete(
                {'project_group_id': project_group.project_group_id,
                 'domain_id': self.domain.domain_id},
                metadata=(('token', self.token),)
            )
            print(f'>> delete project group: {project_group.name} ({project_group.project_group_id})')

    def _create_project_group(self, name=None):
        if name is None:
            name = 'ProjectGroup-' + utils.random_string()[0:5]

        params = {
            'name': name,
            'tags': {'aa': 'bb'},
            'domain_id': self.domain.domain_id
        }

        self.project_group = self.identity_v1.ProjectGroup.create(
            params,
            metadata=(('token', self.token),)
        )

        self.project_groups.append(self.project_group)
        self.assertEqual(self.project_group.name, params['name'])

    def _create_project(self, project_group_id, name=None):
        if name is None:
            name = 'Project-' + utils.random_string()[0:5]

        params = {
            'name': name,
            'project_group_id': project_group_id,
            'tags': {'aa': 'bb'},
            'domain_id': self.domain.domain_id
        }

        self.project = self.identity_v1.Project.create(
            params,
            metadata=(('token', self.token),)
        )

        self.projects.append(self.project)
        self.assertEqual(self.project.name, params['name'])

    def _create_region(self, name=None, region_type='AWS', region_code=None):
        if name is None:
            name = 'Region-' + random_string()[0:5]

        if region_code is None:
            region_code = 'region-' + random_string()[0:5]

        params = {
            'name': name,
            'region_code': region_code,
            'region_type': region_type,
            'domain_id': self.domain.domain_id
        }

        self.region = self.inventory_v1.Region.create(
            params,
            metadata=(('token', self.token),))

        self.regions.append(self.region)
        self.assertEqual(self.region.name, params['name'])

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

    def test_create_device(self, device_type_id=None):
        """ Create Device Type
        """
        if device_type_id is None:
            self.test_create_device_type()

        data = {
            'abc': 'def',
            'xxx': 'yyy'
        }

        params = {
            'device_type_id': self.device_type.device_type_id,
            'data': data,
            'reference': {
                'resource_id': 'xxxyyyyzzz',
                'external_link': 'http://aaaaa.com/xxxyyyzzz'
            },
            'tags': {
                'description': 'test'
            },
            'domain_id': self.domain.domain_id
        }

        self.device = self.inventory_v1.Device.create(
            params, metadata=(('token', self.token),)
        )

        self._print_data(self.device, 'test_create_device')

        self.devices.append(self.device)
        self.assertEqual(MessageToDict(self.device.data), data)

    def test_update_device_data(self):
        self.test_create_device()

        data = {
            'ABC': 'DEF',
            'XXX': 'YYY',
            'ZZZ': '123',
            'abc': 'CHANGED'
        }

        param = {
            'device_id': self.device.device_id,
            'data': data,
            'domain_id': self.domain.domain_id,
        }
        self.device = self.inventory_v1.Device.update(
            param,
            metadata=(('token', self.token),)
        )

        self._print_data(self.device, 'test_update_device_metadata')

    def test_update_device_project(self):
        self.test_create_device()

        self._create_project_group()
        self._create_project(self.project_group.project_group_id)

        param = {
            'device_id': self.device.device_id,
            'project_id': self.project.project_id,
            'domain_id': self.domain.domain_id
        }
        self.device = self.inventory_v1.Device.update(
            param,
            metadata=(('token', self.token),)
        )

        self._print_data(self.device, 'test_update_device_project')

    def test_update_device_region(self):
        self.test_create_device()

        self._create_region()

        param = {
            'device_id': self.device.device_id,
            'region_code': self.region.region_code,
            'region_type': self.region.region_type,
            'domain_id': self.domain.domain_id,
        }

        self.device = self.inventory_v1.Device.update(param, metadata=(('token', self.token),))
        self._print_data(self.device, 'test_update_device_region')

    def test_update_device_tags(self):
        self.test_create_device()

        tags = {
            random_string(): random_string(),
            random_string(): random_string()
        }
        param = {
            'device_id': self.device.device_id,
            'tags': tags,
            'domain_id': self.domain.domain_id,
        }

        self.device = self.inventory_v1.Device.update(param, metadata=(('token', self.token),))
        self.assertEqual(MessageToDict(self.device.tags), tags)

    def test_get_device_type(self):
        self.test_create_device()
        self.test_create_device()

        param = {
            'device_id': self.device.device_id,
            'domain_id': self.domain.domain_id
        }

        device = self.inventory_v1.Device.get(param, metadata=(('token', self.token),))
        self.assertEqual(self.device.device_id, device.device_id)

    def test_list_devices(self):
        self.test_create_device()
        self.test_create_device()
        self.test_create_device()

        param = {
            'device_id': self.device.device_id,
            'domain_id': self.domain.domain_id
        }

        devices = self.inventory_v1.Device.list(param, metadata=(('token', self.token),))

        self.assertEqual(1, devices.total_count)

    def test_list_devices_id(self):
        self.test_create_device()
        self.test_create_device()
        self.test_create_device()
        self.test_create_device()
        self.test_create_device()
        self.test_create_device()

        param = {
            'device_id': self.device.device_id,
            'domain_id': self.domain.domain_id
        }

        devices = self.inventory_v1.Device.list(param, metadata=(('token', self.token),))
        self._print_data(devices, 'test_list_device_id')
        self.assertEqual(1, devices.total_count)

    def test_list_devices_device_type(self):
        self.test_create_device_type()
        device_type_id = self.device_type.device_type_id

        self.test_create_device(device_type_id=device_type_id)
        self.test_create_device(device_type_id=device_type_id)
        self.test_create_device(device_type_id=device_type_id)
        self.test_create_device()
        self.test_create_device()
        self.test_create_device()

        param = {
            'device_type_id': device_type_id,
            'domain_id': self.domain.domain_id
        }

        devices = self.inventory_v1.Device.list(param, metadata=(('token', self.token),))
        self._print_data(devices, 'test_list_device_id')
        self.assertEqual(3, devices.total_count)

    def test_list_query(self):
        self.test_create_device()
        self.test_create_device()
        self.test_create_device()
        self.test_create_device()
        self.test_create_device()
        self.test_create_device()

        param = {
            'domain_id': self.domain.domain_id,
            'query': {
                'filter': [
                    {
                        'k': 'device_id',
                        'v': list(map(lambda device: device.device_id, self.devices)),
                        'o': 'in'
                    }
                ]
            }
        }

        devices = self.inventory_v1.Device.list(param, metadata=(('token', self.token),))

        print(devices)
        self.assertEqual(len(self.devices), devices.total_count)

    def test_stat_device(self):
        self.test_list_query()

        params = {
            'domain_id': self.domain.domain_id,
            'query': {
                'aggregate': {
                    'group': {
                        'keys': [{
                            'key': 'device_id',
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

        result = self.inventory_v1.Device.stat(
            params, metadata=(('token', self.token),))

        self._print_data(result, 'test_stat_device')


if __name__ == "__main__":
    unittest.main(testRunner=RichTestRunner)

