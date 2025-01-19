from typing import Union, Any, List

from maya.api import OpenMaya as om

from rig._lib import node as nde


class Plug(om.MPlug):

    @classmethod
    def fromString(cls, value: str) -> 'Plug':

        selList = om.MSelectionList()
        selList.add(value)
        return cls(selList.getPlug(0))

    def connectedTo(self, *args, **kwargs) -> List['Plug']:

        plugs = []
        for item in super().connectedTo(*args, **kwargs) or []:
            plugs.append(self.__class__(item))

        return plugs

    def proxied(self, *args, **kwargs) -> List['Plug']:
        plugs = []
        for plug in self.proxied():
            plugs.append(plug)

        return plugs

    def source(self):
        return Plug(super().source())

    def destinations(self) -> List['Plug']:
        plugs = []
        for item in super().destinations() or []:
            plugs.append(self.__class__(item))

        return plugs

    def __getitem__(self, value: Union[str, int]) -> 'Plug':

        if self.isCompound and isinstance(value, str):
            for idx in range(self.numChildren()):
                ln = self.child(idx).name()
                sn = self.child(idx).partialName(useAlias=True)

                if value in [ln, sn]:
                    return self.__class__(self.child(idx))

        elif self.isCompound and isinstance(value, int):
            return self.__class__(self.child(value))

        elif self.isArray and isinstance(value, int):
            return self.__class__(self.elementByLogicalIndex(value))

        return self.__class__()

    def parent(self, *args, **kwargs):
        return self.__class__(super().parent(*args, **kwargs))

    def child(self, *args, **kwargs):
        return self.__class__(super().child(*args, **kwargs))

    def node(self) -> None:
        return nde.Node(super().node())

    def __setitem__(
            self,
            key: str,
            value: Any
            ) -> None:
        # TODO: need to fix this part with the * operator
        if isinstance(value, tuple):
            self[key].set(*value)

        else:
            self[key].set(value)

    def __str__(self) -> str:
        attr_name = self.partialName(
                includeNodeName=True,
                useLongNames=True,
                # useFullAttributePath=True
                )
        return attr_name

    def __repr__(self) -> str:
        attr_name = self.partialName(
                includeNodeName=True,
                useLongNames=True,
                useFullAttributePath=True
                )

        return f'Plug.fromString("{attr_name}")'

    def set(self, *value: Any) -> None:

        if isinstance(value[0], om.MPlug):
            self.__class__(value).connect(self)

        elif self.isCompound or self.isArray:
            for idx, val in enumerate(value):

                if self.isCompound:
                    self.child(idx).set(val)

                if self.isArray:
                    self.elementByLogicalIndex(idx).set(val)

        elif len(value) == 16:
            value = om.MMatrix(value)
            matrixData = om.MFnMatrixData()
            matobj = matrixData.create(value)
            self.setMObject(matobj)

        elif isinstance(value[0], int):
            self.setInt(value[0])

        elif isinstance(value[0], float):
            self.setDouble(value[0])

        elif isinstance(value[0], bool):
            self.setBool(value[0])

        elif isinstance(value[0], str):
            self.setString(value[0])

        elif isinstance(value[0], om.MMatrix):
            matrixData = om.MFnMatrixData()
            matobj = matrixData.create(value[0])
            self.setMObject(matobj)

    def connect(self, other: 'Plug', force=False) -> None:

        modifier = om.MDGModifier()
        if other.isDestination and force:
            modifier.disconnect(other.source(), other)

        elif other.isDestination:
            raise NameError(f"plug {other} is already connected")

        modifier.connect(self, other)
        modifier.doIt()

    def disconnect(self, other: 'Plug') -> None:
        modifier = om.MDGModifier()
        modifier.disconnect(self, other)
        modifier.doIt()

    def __rshift__(self, other) -> None:
        self.connect(other, force=True)

    def __lshift__(self, other) -> None:

        modifier = om.MDGModifier()
        if self.isDestination:
            modifier.disconnect(self.source(), self)

        modifier.connect(other, self)
        modifier.doIt()
