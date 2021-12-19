import copy
import os

import toolcache


def get_config_path(config_path=None, config_path_env_var=None):
    if config_path is not None:
        return config_path

    elif config_path_env_var is not None and config_path_env_var in os.environ:
        config_path = os.environ[config_path_env_var]
        if config_path == '' or config_path is None:
            raise Exception(
                'ENV variable ' + config_path_env_var + ' is invalid value'
            )
        return config_path

    else:
        return None


@toolcache.cache(cachetype='memory')
def get_config(
    config_path_env_var=None,
    config_path=None,
    config_spec=None,
    default_config_values=None,
    config_required=False,
    config_key_variables=None,
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
            'config required, put config in path in environment variable '
            + config_path_env_var
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
    if config_spec is not None:
        extra_keys = set(config.keys()) - set(config_spec.keys())
        if len(extra_keys) > 0:
            raise Exception('unknown keys in config: ' + str(extra_keys))

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

