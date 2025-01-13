from typing import Union, List, Dict

from maya import cmds
from maya.api import OpenMaya as om

from rig._lib.graph import Graph
from rig._lib.node import Node
from rig._lib.plug import Plug


class Container(om.MObject):

    @classmethod
    def create(cls, name=None):
        obj = om.MFnDependencyNode().create('container', name)
        return cls(obj)

    def __init__(self, entry: Union[str, om.MObject]) -> None:

        if isinstance(entry, str):
            selList = om.MSelectionList()
            selList.add(entry)
            super().__init__(selList.getDependNode(0))

        else:
            super().__init__(entry)

        self.fnContainer = om.MFnContainerNode(self)

    @property
    def name(self) -> str:

        if self.fnContainer.hasUniqueName():
            return self.fnContainer.name()
        else:
            return self.fnContainer.absoluteName()

    @name.setter
    def name(self, value: str) -> None:
        self.fnContainer.setName(value)

    @property
    def parent(self) -> 'Container':
        return self.__class__(self.fnContainer.getParentContainer())

    @property
    def children(self) -> List['Container']:
        return_list = []
        for item in self.fnContainer.getSubcontainers():
            return_list.append(self.__class__(item))

        return return_list

    @property
    def nodes(self) -> Graph:

        sel = Graph()
        for item in self.fnContainer.getMembers():
            sel.add(item)
        return sel

    @property
    def publishNodes(self) -> Dict[str, Node]:
        names, nodes = self.fnContainer.getPublishedNodes(0)
        nodes = [Node(node) for node in nodes]
        return dict(zip(names, nodes))

    @property
    def publishPlugs(self) -> Dict[str, Plug]:
        plugs, names = self.fnContainer.getPublishedPlugs()
        plugs = [Plug(plug) for plug in plugs]
        return dict(zip(names, plugs))

    @property
    def current(self) -> bool:
        return self.fnContainer.isCurrent()

    @current.setter
    def current(self, current: bool) -> None:
        self.fnContainer.makeCurrent(current)

    @property
    def rootTransform(self) -> None:
        return Node(self.fnContainer.getRootTransform())

    def createNode(self, typ, name=None, parent=None) -> Node:

        node = Node.create(typ, name=name, parent=parent)
        self.addNode(node)
        return node

    def addNode(self, node: str | om.MObject) -> None:

        node = Node(node)
        cmds.container(self.name, addNode=str(node), e=True)
