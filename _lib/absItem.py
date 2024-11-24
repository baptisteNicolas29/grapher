from abc import ABC, abstractmethod

from rig._lib import node as rnode
from rig._lib import absModule as amodule


class AbcItem(ABC, rnode.Node):

    IDENTIFIER: str = None

    @classmethod
    def create(
            cls,
            name: str = None,
            module: rnode.Node = None
            ) -> 'AbcItem':
        ...

    @abstractmethod
    def build(self) -> rnode.Node: ...
