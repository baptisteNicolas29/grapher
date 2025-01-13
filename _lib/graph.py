from typing import List, Any, Union, Optional

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

    @classmethod
    def getDagRoots(
            cls,
            nodes: Union[List[str], List[Node], om.MSelectionList],
            safe=True
            ) -> 'Graph':

        if isinstance(nodes, list):
            tmp = Graph()

            for node in nodes:
                tmp.add(node)

            node = tmp

        elif isinstance(nodes, om.MSelectionList):
            nodes = cls(nodes)

        previous = cls()
        roots = cls()
        for item in nodes:
            previous.add(item)

            if (not safe) and (not item.hasFn(om.MFn.MFnDagNode)):
                raise TypeError(f'{node} is not a dagNode')

            if safe and (not item.hasFn(om.MFn.kDagNode)):
                continue

            is_child = False
            mfnDagNode = om.MFnDagNode(item)
            for other in nodes - previous:
                is_child |= mfnDagNode.isChildOf(other)

            if not is_child:
                roots.add(item)

        return roots

    @classmethod
    def getChildren(
            cls,
            node: Union[str, om.MObject],
            graph: Union[om.MSelectionList, List[str], List[Node]]
            ) -> 'Graph':

        node = Node(node)
        if not node.hasFn(om.MFn.kDagNode):
            return

        if isinstance(graph, om.MSelectionList):
            graph = cls(graph)

        elif isinstance(graph, list):
            tmp = Graph()

            for node in graph:
                tmp.add(node)

            graph = tmp

        else:
            raise TypeError('graph need to be list or om.MSelectionList')

        # clear graph
        if node in graph:
            node_graph = Graph()
            node_graph.add(node)
            graph = graph - node_graph

        childrens = cls()
        for other in graph:
            otherDagNode = om.MFnDagNode(other)

            if otherDagNode.isChildOf(node):
                childrens.add(other)

        return childrens

    @classmethod
    def getParents(
            cls,
            node: Union[str, om.MObject],
            graph: Union[om.MSelectionList, List[str], List[Node]]
            ) -> 'Graph':

        node = Node(node)

        if isinstance(graph, om.MSelectionList):
            graph = cls(graph)

        elif not node.hasFn(om.MFn.kDagNode):
            return

        elif isinstance(graph, list):
            tmp = Graph()

            for node in graph:
                tmp.add(node)

            graph = tmp

        else:
            raise TypeError('second argument need to be list or om.MSelectionList')

        # clear graph
        if node in graph:
            node_graph = Graph()
            node_graph.add(node)
            graph = graph - node_graph

        dagNode = om.MFnDagNode(node)
        dagPath = dagNode.getPath()

        parents = cls()
        for other in graph:

            if dagNode.isChildOf(other):
                parents.add(other)

        return parents

    @classmethod
    def getDirectChildren(
            cls,
            node: Union[str, om.MObject],
            graph: Union[om.MSelectionList, List[str], List[Node]]
            ) -> 'Graph':

        childrens = cls.getChildren(node, graph)
        childrens_copy = cls().copy(childrens)

        to_remove = cls()
        for child in childrens_copy:
            for subChild in cls.getChildren(child, graph):
                to_remove.add(subChild)

        return childrens - to_remove

    @classmethod
    def getDirectParent(
            cls,
            node: Union[str, om.MObject],
            graph: Union[om.MSelectionList, List[str], List[Node]]
            ) -> Optional[Node]:

        parents = cls.getParents(node, graph)
        parents_copy = cls().copy(parents)

        to_remove = cls()
        for par in parents_copy:
            for subParent in cls.getParents(par, graph):
                to_remove.add(subParent)

        if parent := parents - to_remove:
            return parent.get(0)

    @property
    def dagRoots(self) -> 'Graph':
        return self.getDagRoots(self, safe=True)

    def children(self, node: Union[str, om.MObject]) -> 'Graph':
        return self.getChildren(node, self)

    def parents(self, node: Union[str, om.MObject]) -> 'Graph':
        return self.getParents(node, self)

    def directChildren(self, node: Union[str, om.MObject]) -> 'Graph':
        return self.getChildren(node, self)

    def directParents(self, node: Union[str, om.MObject]) -> Optional[Node]:
        return self.getParents(node, self)

    @staticmethod
    def __initRegistred(value: str) -> Any:
        return Node(value)

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

    def __repr__(self) -> str:
        class_name = self.__class__.__name__
        return f'{class_name}.ls({[str(x) for x in self]})'

    def get(self, value: Union[str, int]) -> Any:
        return self.__initRegistred(self.getDependNode(value))

    def __and__(self, other: om.MSelectionList) -> 'Graph':
        '''
        intersection
        '''
        print(type(self), type(other))
        if not isinstance(other, om.MSelectionList):
            raise TypeError(f'can not intersect Graph and {type(other)}')

        final_lst = self.__class__().copy(self)
        final_lst = final_lst.intersect(other)
        return self.__class__(final_lst)

    def __or__(self, other: om.MSelectionList) -> 'Graph':
        '''
        union
        '''
        copy = self.__class__().copy(self)
        return copy(self).merge(other)

    def __xor__(self, other: om.MSelectionList) -> 'Graph':
        '''
        symetrical difference
        '''
        copy = self.__class__().copy(self)
        return copy.merge(other, strategy=om.MSelectionList.kXORWithList)

    def __iter__(self) -> Union[Node, Plug]:
        for idx in range(self.length()):
            yield self.get(idx)

    def __contains__(self, item: om.MObject | om.MPlug | om.MDagPath) -> bool:
        return self.hasItem(item)

    def __sub__(self, other: om.MSelectionList) -> 'Graph':
        copy = self.__class__().copy(self)
        return copy.merge(other, strategy=om.MSelectionList.kRemoveFromList)
