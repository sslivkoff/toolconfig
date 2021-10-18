import copy
import os

import yaml
import toolcache


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
    if (
        config_path is None
        and config_path_env_var is not None
        and config_path_env_var in os.environ
    ):
        config_path = os.environ[config_path_env_var]
        if config_path == '' or config_path is None:
            raise Exception(config_path_env_var + ' is invalid value')

    # load config
    config = None
    if config_path is not None:
        if not os.path.isfile(config_path):
            raise Exception('config file does not exist: ' + str(config_path))
        with open(config_path, 'r') as f:
            config = yaml.load(f, Loader=yaml.CLoader)

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

