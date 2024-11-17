from __future__ import annotations

from collections.abc import Iterable
from collections.abc import Mapping
from enum import Enum
from typing import Any
from typing import get_type_hints


def unpack_enum_types(data: Mapping[str, Any]) -> dict[str, Any]:
    """Creates a shallow copy of `data`, where all `Enum` subclasses are replaced
    with their `value`."""

    res = {}

    for key, value in data.items():
        if issubclass(type(value), Enum):
            value = value.value

        res[key] = value

    return res


def update_from_partial_dict(table: str, object_id: int, data: dict[str, Any]) -> str:
    """Creates an `UPDATE` MySQL statement from a data kwargs."""

    return (
        f"UPDATE `{table}` SET "
        + ", ".join(f"{name} = :{name}" for name in data.keys())
        + f" WHERE id = {object_id}"
    )


def get_model_fields(model: type) -> list[str]:
    """Gets a list of all typed fields from a `dataclass`."""

    return list(get_type_hints(model))


def remove_id_field(values: list[str]) -> list[str]:
    """Takes input from `get_model_fields` and removed the 'id' field if it exists.
    Creates a copy of the output."""

    values = values.copy()
    try:
        values.remove("id")
    except ValueError:
        pass

    return values


def comma_separated(values: Iterable[str]) -> str:
    return ", ".join(values)


def colon_prefixed_comma_separated(values: Iterable[str]) -> str:
    return comma_separated(map(lambda x: f":{x}", values))
