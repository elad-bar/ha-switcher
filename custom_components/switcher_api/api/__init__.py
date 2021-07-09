from enum import Enum
from typing import Dict, List, Set, Union


def _serialize_object(obj: object) -> Dict[str, Union[List[str], str]]:
    """Use for converting enum to primitives and remove not relevant keys ."""
    serialized_dict = dict()  # type: Dict[str, Union[List[str], str]]
    for k, v in obj.__dict__.items():
        if not k == "unparsed_response":
            if isinstance(v, Enum):
                serialized_dict[k] = v.name
            elif isinstance(v, Set):
                serialized_dict[k] = [m.name if isinstance(m, Enum) else m for m in v]
            else:
                serialized_dict[k] = v

    return serialized_dict
