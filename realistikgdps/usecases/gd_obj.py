from realistikgdps.typing.protocols import SupportsStr

def into_gd_obj(obj: dict[SupportsStr, SupportsStr], sep: str = ":") -> str:
    res = ""

    for key, value in obj.items():
        res += f"{key}:{value}:"
    
    return res[:-1]
