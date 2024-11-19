from typing import Union
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
