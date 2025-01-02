from typing import List, Any

from maya import cmds
from maya.api import OpenMaya as om

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
        result = cmds.ls(*args, **kwargs) or []
        return cls(map(cls.__initRegistred, result))

    @staticmethod
    def __initRegistred(value: str) -> Any:
        return Node(value)

    @classmethod
    def listHistory(cls, *args, **kwargs) -> 'Graph':
        """
        desc: this function is a reimplementation of the cmds.listHistory function
        allow user to gathers nodes from string list
        args and kwargs work like cmds.listHistory command
        """
        result = cmds.listHistory(*args, **kwargs) or []
        return cls(map(cls.__initRegistred, result))

    @classmethod
    def listRelatives(cls, *args, **kwargs) -> 'Graph':
        """
        desc: this function is a reimplementation of the cmds.listHistory function
        allow user to gathers nodes from string list
        args and kwargs work like cmds.listHistory command
        """
        print(args, kwargs)
        result = cmds.listRelatives(*args, **kwargs) or []
        return cls(map(cls.__initRegistred, result))
