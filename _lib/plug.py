from typing import Union, Any

from maya.api import OpenMaya as om


class Plug(om.MPlug):

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

    def set(self, *value: Any) -> None:
        print(f'Plug.set -> {value}')

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
