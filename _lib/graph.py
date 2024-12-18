from typing import List, Any

from maya import cmds

from rig._lib.node import Node
# from rig._lib.plug import Plug


class Graph(list):

    @classmethod
    def ls(cls, *args, **kwargs) -> List[Node]:
        """
        desc: this function is a reimplementation of the cmds.ls function
        allow user to gathers nodes from string list
        args and kwargs work like cmds.ls command
        """
        result = cmds.ls(*args, **kwargs)
        return cls(map(cls.__initRegistred, result))

    @classmethod
    def __initRegistred(self, value: str) -> Any:
        return Node(value)

    @classmethod
    def listHistory(cls, *args, **kwargs) -> 'Graph':
        return cls(cmds.listHistory(*args, *kwargs))

    @classmethod
    def listRelatives(cls, *args, **kwargs) -> 'Graph':
        return cls(cmds.listRelatives(*args, *kwargs))
