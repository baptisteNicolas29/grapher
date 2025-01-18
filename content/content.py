from typing import List, Any


class Content:

    def __init__(self) -> None:
        self.__content = {}

    def append(self, item: Any) -> None:
        ...

    def remove(self, item: Any) -> None:
        ...

    def __getitem__(self, key: str) -> Any:
        ...

    def __setitem__(self, key: str) -> Any:
        ...

    def keys(self) -> List[str]:
        ...

    def values(self) -> List[Any]:
        ...

    def load_from_path(self) -> None:
        ...
