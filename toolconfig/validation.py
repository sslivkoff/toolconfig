import typing
import warnings

import pydantic

from . import spec


def validate_config(
    config: dict,
    config_spec: spec.ConfigSpec,
    validate: typing.Literal['raise', 'warn', False],
):

    if not validate:
        return None

    # determine whether config conforms to spec
    is_valid = conforms_to_spec(data=config, spec=config_spec)

    # perform action if not vaild
    if not is_valid:
        if validate == 'raise':
            raise ValueError('config does not conform to spec')
        elif validate == 'warn':
            warnings.warn('config does not conform to spec')
        else:
            raise Exception('unknown validate action: ' + str(validate))


def conforms_to_spec(data: dict, spec: dict) -> bool:

    # check using pydantic
    if hasattr(spec, '__annotations__') and hasattr(spec, '__name__'):
        pydantic_model = typed_dict_to_pydantic_model(typed_dict=spec)
        try:
            pydantic_model(**data)
            return True
        except pydantic.ValidationError:
            return False

    # check that keys match
    elif isinstance(spec, dict):
        extra_keys = set(data.keys()) - set(spec.keys())
        return len(extra_keys) == 0

    else:
        raise Exception('unknown spec type: ' + str(spec))


def typed_dict_to_pydantic_model(
    typed_dict: dict,
) -> pydantic.main.ModelMetaclass:

    if not hasattr(typed_dict, '__annotations__') or not hasattr(
        typed_dict, '__name__'
    ):
        raise Exception('not a valid TypedDict')

    fields = {k: (v, ...) for k, v in typed_dict.__annotations__.items()}

    return pydantic.create_model(typed_dict.__name__, **fields)  # type: ignore

