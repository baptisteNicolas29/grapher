from typing import Union, Any

from maya.api import OpenMaya as om
from rig._lib.plug import Plug


class Node(om.MObject):

    @classmethod
    def create(cls, typ, name=None, parent=None):

        if parent:
            obj = om.MFnDagNode().create(typ, name=name, parent=parent)

        else:
            obj = om.MFnDependencyNode().create(typ, name)

        return cls(obj)

    def __init__(self, entry: Union[str, om.MObject]) -> None:

        if isinstance(entry, str):
            selList = om.MSelectionList()
            selList.add(entry)
            super().__init__(selList.getDependNode(0))
        else:
            super().__init__(entry)

        self.dependencyNode = om.MFnDependencyNode(self)

    def __str__(self) -> str:
        return self.name

    @property
    def parent(self) -> None:

        fn = om.MFnDagNode(self)
        items = []
        for idx in range(fn.parentCount()):
            items.append(self.__class__(fn.parent(idx)))

        return items

    @property
    def children(self) -> None:

        fn = om.MFnDagNode(self)
        items = []
        for idx in range(fn.childCount()):
            items.append(self.__class__(fn.child(idx)))

        return items

    @property
    def name(self) -> str:
        return self.dependencyNode.uniqueName()

    @name.setter
    def name(self, value: str) -> None:
        self.dependencyNode.setName(value)

    def __getitem__(self, item: Union[str, int]) -> 'Plug':

        if self.hasFn(om.MFn.kContainer):
            container = om.MFnContainerNode(self)
            plugs, names = container.getPublishedPlugs()

            for plug, name in zip(plugs, names):
                if item == name:
                    return Plug(plug)

        return Plug(self.dependencyNode.findPlug(item, True))

    def __setitem__(
            self,
            key: str,
            value: Any
            ) -> None:

        self[key].set(*value)
