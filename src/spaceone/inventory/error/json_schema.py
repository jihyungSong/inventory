from spaceone.core.error import *

class ERROR_DUPLICATE_DEVICE_TYPE_SCHEMA(ERROR_BASE):
    _message = 'Duplicate schema with parent device type template (key={key})'


class ERROR_INVALID_SCHEMA(ERROR_BASE):
    _message = 'Schema format(JSON SCHEMA) is invalid. (key = {key})'


class ERROR_MODIFY_SCHEMA_TYPE(ERROR_BASE):
    _message = 'Can not modify data type in JSON SCHEMA. (key = {key}, type = {type})'
