import os
import typing


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

    # validate input combination
    if config_path is not None and config_path_env_var is not None:
        raise Exception('cannot specify config_path and config_path_env_var')

    # get config_path from environmental variable
    if config_path_env_var is not None:
        config_path = env_var_to_config_path(config_path_env_var)

    # validate config_path
    if raise_if_unset and not config_path_is_set(config_path=config_path):
        if config_path_env_var is not None:
            raise Exception(
                'config environment variable not set: '
                + str(config_path_env_var)
            )
        else:
            raise Exception('config_path is not set')
    if raise_if_dne and not config_path_exists(config_path=config_path):
        raise Exception('config_path does not exist: ' + str(config_path))

    return config_path


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

