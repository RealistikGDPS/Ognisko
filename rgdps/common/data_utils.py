from rgdps.common.protocols import HasIntValue

def enum_int_list(l: list[HasIntValue]) -> list[int]:
    return [x.value for x in l]

