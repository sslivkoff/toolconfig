import typing


ConfigSpec = dict
ConfigData = typing.MutableMapping[str, typing.Any]

ValidationOption = typing.Literal['raise', 'warn', False]
OverwriteOption = typing.Literal[True, False, 'prompt']


class GetConfigKwargs(typing.TypedDict, total=False):
    config_path_env_var: typing.Optional[str]
    config_path: typing.Optional[str]
    default_config_path: typing.Optional[str]
    config_spec: typing.Optional[ConfigSpec]
    default_config_values: typing.Optional[dict]
    config_required: bool
    config_variables: typing.Optional[dict[str, typing.Mapping]]
    validate: typing.Literal['raise', 'warn', False]

