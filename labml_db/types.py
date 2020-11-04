from typing import List, Dict, Union

Primitive = Union[Dict[str, 'Primitive'], List['Primitive'], int, str, float, bool, None]
ModelDict = Dict[str, Primitive]

