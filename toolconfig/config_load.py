import copy
import os
import typing
import warnings

import toolcache

from . import toolbox


ConfigSpec = dict


def env_var_to_config_path(config_path_env_var: str) -> typing.Optional[str]:
    return os.environ.get(config_path_env_var)


def config_path_is_set(
    *,
    config_path: typing.Optional[str] = None,
    config_path_env_var: typing.Optional[str] = None,
) -> bool:

    if config_path_env_var is not None:
        config_path = env_var_to_config_path(config_path_env_var)

    return config_path not in [None, '']


def config_path_exists(
    *,
    config_path: typing.Optional[str] = None,
    config_path_env_var: typing.Optional[str] = None,
) -> bool:

    if config_path_env_var is not None:
        config_path = env_var_to_config_path(config_path_env_var)

    return config_path is not None and os.path.isfile(config_path)


def get_config_path(
    *,
    config_path: typing.Optional[str] = None,
    config_path_env_var: typing.Optional[str] = None,
    raise_if_unset: bool = True,
    raise_if_dne: bool = True,
) -> typing.Optional[str]:

    if config_path_env_var is not None:
        config_path = env_var_to_config_path(config_path_env_var)

    if raise_if_unset and not config_path_is_set(config_path=config_path):
        raise Exception('path is not set')
    if raise_if_dne and not config_path_exists(config_path=config_path):
        raise Exception('path does not exist')

    return config_path


@toolcache.cache(cachetype='memory')
def get_config(
    config_path_env_var: typing.Optional[str] = None,
    config_path: typing.Optional[str] = None,
    config_spec: typing.Optional[ConfigSpec] = None,
    default_config_values: typing.Optional[dict] = None,
    config_required: bool = False,
    config_key_variables: typing.Optional[dict] = None,
    validate: typing.Literal['raise', 'warn', False] = False,
):

    # get config path
    config_path = get_config_path(
        config_path=config_path,
        config_path_env_var=config_path_env_var,
    )

    # load config
    config = None
    if config_path is not None:
        if not os.path.isfile(config_path):
            raise Exception('config file does not exist: ' + str(config_path))
        config = load_file(config_path)

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
            validate_config(
                config=config, config_spec=config_spec, validate=validate
            )
    return config


def load_file(config_path):
    with open(config_path, 'r') as f:
        if config_path.endswith('.json'):
            import json

            return json.load(f)
        elif config_path.endswith('.yaml'):
            import yaml

            return yaml.load(f, Loader=yaml.CLoader)
        else:
            raise Exception('unknown config format')


def validate_config(
    config: dict,
    config_spec: ConfigSpec,
    validate: typing.Literal['raise', 'warn', False],
):

    if not validate:
        return None

    # determine whether config conforms to spec
    is_valid = toolbox.conforms_to_spec(data=config, spec=config_spec)

    # perform action if not vaild
    if not is_valid:
        if validate == 'raise':
            raise ValueError('config does not conform to spec')
        elif validate == 'warn':
            warnings.warn('config does not conform to spec')
        else:
            raise Exception('unknown validate action: ' + str(validate))

