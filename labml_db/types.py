from typing import List, Dict, Union, Tuple

Primitive = Union[Dict[str, 'Primitive'], List['Primitive'], int, str, float, bool, None]
ModelDict = Dict[str, Primitive]
# {Property: (value, equal/not_equal)}
QueryDict = Dict[str, Tuple[Union[List['Primitive'], int, str, float, bool], bool]]
SortDict = List[Tuple[str, bool]]
