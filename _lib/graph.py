from typing import List, Any, Union

from maya import cmds
from maya.api import OpenMaya as om

from rig._lib.node import Node
from rig._lib.plug import Plug


class Graph(om.MSelectionList):

    @classmethod
    def ls(cls, *args, **kwargs) -> List[Node]:
        """
        desc: this function is a reimplementation of the cmds.ls function
        allow user to gathers nodes from string list
        args and kwargs work like cmds.ls command
        """
        result = cmds.ls(*args, **kwargs) or []
        lst = cls()
        for item in result:
            lst.add(item)

        return lst

    def createNode(self, typ: str, name=None, parent=None) -> Node:
        """
        desc: this function allow node creation from Graph
        created node will be added to graph
        :param str: typ type of the created node
        :param str: name name of the created node
        :param Node: parent parent of the created node
        :return Node: created Node
        """
        node = Node.create(typ, name=name, parent=parent)
        self.add(node)
        return node

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

        lst = cls()
        for item in result:
            lst.add(item)

        return lst

    @classmethod
    def listRelatives(cls, *args, **kwargs) -> 'Graph':
        """
        desc: this function is a reimplementation of the cmds.listHistory function
        allow user to gathers nodes from string list
        args and kwargs work like cmds.listHistory command
        """
        print(args, kwargs)
        result = cmds.listRelatives(*args, **kwargs) or []

        lst = cls()
        for item in result:
            lst.add(item)

        return lst

    def get(self, value: Union[str, int]) -> Any:
        return self.__initRegistred(self.getDependNode(value))

    def __and__(self, other: om.MSelectionList) -> 'Graph':
        '''
        intersection
        '''
        print(type(self), type(other))
        if not isinstance(other, om.MSelectionList):
            raise TypeError(f'can not intersect Graph and {type(other)}')

        final_lst = self.intersect(other)
        return self.__class__(final_lst)

    def __or__(self, other: om.MSelectionList) -> 'Graph':
        '''
        union
        '''
        if not isinstance(other, om.MSelectionList):
            raise TypeError(f'can not unify Graph and {type(other)}')

        return self.__class__(self.merge(other))

    """
    def __xor__(self, other: om.MSelectionList) -> 'Graph':
        '''
        symetrical difference
        '''
        if not isinstance(other, om.MSelectionList):
            raise TypeError(f'can not make symetrical difference between Graph and {type(other)}')

        return self
    """

    def __iter__(self) -> Union[Node, Plug]:
        for idx in range(self.length()):
            yield self.get(idx)

    def __contains__(self, item: om.MObject | om.MPlug | om.MDagPath) -> bool:
        return self.hasItem(item)
