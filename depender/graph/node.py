from typing import List, Union, Optional


Attribute_Type = Optional[Union[str, float, "Node"]]


class Node:
    NodeProperties = ["name", "label", "x", "y", "size", "width", "height", "index", "change",
                      "shift", "modifier", "thread", "parent", "ancestor",
                      "leftmost_sibling", "left_sibling", "right_sibling"]

    def __init__(self, name: str, **kwargs: Attribute_Type) -> None:
        self.name = name  # type: str
        self.label = kwargs.get("label", "")  # type: str
        self.type = kwargs.get("type", None)  # type: Optional[str]
        self.x = kwargs.get("x", 0)  # type: float
        self.y = kwargs.get("y", 0)  # type: float
        self.size = kwargs.get("size", 0)  # type: float
        self.width = kwargs.get("width", 0)  # type: float
        self.height = kwargs.get("height", 0)  # type: float
        self.index = kwargs.get("index", 1)  # type: int
        self.change = kwargs.get("change", 0)  # type: float
        self.shift = kwargs.get("shift", 0)  # type: float
        self.modifier = kwargs.get("modifier", 0)  # type: float
        self.thread = None  # type: Optional[Node]
        self.parent = None  # type: Optional[Node]
        self.children = list()  # type: List[Node]
        self.ancestor = self  # type: Node
        self.leftmost_sibling = None  # type: Optional[Node]
        self.left_sibling = None  # type: Optional[Node]

    def __getitem__(self, item: str) -> Attribute_Type:
        return getattr(self, item)

    def __setitem__(self, key: str, value: Attribute_Type) -> None:
        if key not in self.NodeProperties:
            raise AttributeError(f"'Node' object has no attribute '{key}'")
        setattr(self, key, value)

    def __repr__(self):
        return f"(Name: '{self.name}', Label: '{self.label}', \n" \
            f"X: '{self.x}', Y: '{self.y}', Width: '{self.width}', Height: '{self.height}')"


