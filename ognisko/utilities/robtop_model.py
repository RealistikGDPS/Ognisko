from __future__ import annotations

from typing import Any
from typing import Callable

from pydantic import BaseModel
from pydantic import Field
from pydantic import ConfigDict

def dumps(
    obj: dict[str, Any],
    deliminer: str = ":",
) -> str:
    return deliminer.join(f"{key}{deliminer}{value}" for key, value in obj.items())


def loads[
    KT,
    VT,
](
    data: str,
    sep: str = ":",
    key_cast: Callable[[str], KT] = int,
    value_cast: Callable[[str], VT] = str,
) -> dict[KT, VT]:
    data_split = data.split(sep)

    if len(data_split) % 2 != 0:
        raise ValueError("Data does not have matching key/value pairs.")

    data_iter = iter(data_split)

    return {
        key_cast(key): value_cast(value) for key, value in zip(data_iter, data_iter)
    }


def Key(default=..., *, index: int = 0):
    return Field(default=default, alias=str(index))

class RobTopModel(BaseModel):
    """A Pydantic model that can be serialised to and from a RobTop string.
    
    Example usage:
    ```python
    
    class UserObject(RobTopModel):
        id: int = Key(index=1)
        name: str = Key(index=2)
        age: int = Key(index=4)

    user = UserObject.from_robtop("2:Grzegorz Brzęczyszczykiewicz:4:21:1:3")
    print(user.id)      # 3
    print(user.name)    # Grzegorz Brzęczyszczykiewicz
    print(user.age)     # 21
    ```
    """

    model_config = ConfigDict(
        populate_by_name=True,
    )

    @staticmethod
    def from_robtop(data: str, deliminer: str = ":") -> RobTopModel:
        data_dictionary = loads(data, deliminer, key_cast=str, value_cast=str)

        return RobTopModel(**data_dictionary)
    
    def to_robtop(self, deliminer: str = ":") -> str:
        return dumps(
            self.model_dump(by_alias=True),
            deliminer=deliminer,
        )

