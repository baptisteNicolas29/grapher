from typing import Union, List, Dict, Optional

from maya import cmds
from maya.api import OpenMaya as om

from .graph import Graph
from .node import Node
from .plug import Plug


class Container(Node):

    @classmethod
    def create(cls, name=None):
        obj = om.MFnDependencyNode().create('container', name)
        return cls(obj)

    @classmethod
    def containerize(
            cls,
            graph: Graph,
            name: str | None = None,
            setRootTransform: bool = False
            ) -> 'Container':

        container = cls.create(name)
        for node in graph:
            container.addNode(node)

        if setRootTransform:
            if dagRoots := graph.dagRoots:
                container.rootTransform = dagRoots.get(0)

        return container

    def __init__(self, entry: Union[str, om.MObject]) -> None:

        super().__init__(entry)
        self.fnContainer = om.MFnContainerNode(self)

    def __repr__(self) -> str:
        return f'Container("{self.name}")'

    def __str__(self) -> str:
        return self.name

    @property
    def parent(self) -> Optional['Container']:
        if parent := self.fnContainer.getParentContainer():
            if parent.isNull():
                return
            return self.__class__(parent)

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

    def __publishNodes(self, attr) -> Dict[str, Node]:
        names, nodes = self.fnContainer.getPublishedNodes(attr)
        nodes = [Node(node) for node in nodes]
        return dict(zip(names, nodes))

    @property
    def publishParentAnchor(self) -> Dict[str, Node]:
        return self.__publishNodes(self.fnContainer.kParentAnchor)

    @property
    def publishChildAnchor(self) -> Dict[str, Node]:
        return self.__publishNodes(self.fnContainer.kChildAnchor)

    @property
    def publishNodes(self) -> Dict[str, Node]:
        return self.__publishNodes(self.fnContainer.kGeneric)

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

    @rootTransform.setter
    def rootTransform(self, node: str | Node | None) -> None:

        if node is None:
            src = Node(self)['rt'].source()
            if src.isNull:
                return
            Plug(src).disconnect(Node(self.name)['rt'])
            return

        node = Node(node)

        if node not in self.nodes:
            raise NameError(f'{node} is not part of the container')

        node['msg'] >> Node(self)['rt']

    def createNode(self, typ, name=None, parent=None) -> Node:

        node = Node.create(typ, name=name, parent=parent)
        self.addNode(node)
        return node

    def addNode(self, node: str | om.MObject) -> None:

        node = Node(node)
        cmds.container(self.name, addNode=str(node), e=True)
