import copy
import os
import typing

import toolcache

from . import filesystem
from . import spec
from . import validation


@toolcache.cache(cachetype='memory')
def get_config(
    config_path_env_var: typing.Optional[str] = None,
    config_path: typing.Optional[str] = None,
    config_spec: typing.Optional[spec.ConfigSpec] = None,
    default_config_values: typing.Optional[dict] = None,
    config_required: bool = False,
    config_key_variables: typing.Optional[dict] = None,
    validate: typing.Literal['raise', 'warn', False] = False,
):

    # get config path
    config_path = filesystem.get_config_path(
        config_path=config_path,
        config_path_env_var=config_path_env_var,
    )

    # load config
    config = None
    if config_path is not None:
        if not os.path.isfile(config_path):
            raise Exception('config file does not exist: ' + str(config_path))
        config = filesystem.load_file(config_path)

    # check if config required
    if config_required and config is None:
        raise Exception(
            'must specify config, might need to set environment variable '
            + str(config_path_env_var)
        )

    # set defaults
    if default_config_values is None:
        default_config_values = {}
    if config is None:
        config = copy.deepcopy(default_config_values)
    for key, value in default_config_values.items():
        config.setdefault(key, value)

    # populate variables
    if config_key_variables is not None:
        for key, variables in config_key_variables.items():
            config[key] = config[key].format(**config)

    # validate spec
    if validate:
        if config_spec is None:
            raise Exception('cannot validate unless config_spec is given')
        else:
            validation.validate_config(
                config=config,
                config_spec=config_spec,
                validate=validate,
            )

    return config

