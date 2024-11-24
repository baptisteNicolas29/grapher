from abc import ABC, abstractmethod

from rig._lib import node as rnode
from rig._lib.absItem import AbcItem


class AbcModule(ABC):

    IDENTIFIER: str = None

    @classmethod
    def create(cls, name: str, rig=None) -> 'AbcModule': ...

    @abstractmethod
    def build(self) -> rnode.Node: ...
