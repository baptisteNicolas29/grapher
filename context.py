from contextlib import contextmanager

from maya import cmds


@contextmanager
def withContainer(containerName=None) -> str:
    current = cmds.container(q=True)

    if containerName:
        container = cmds.container(n=containerName, current=True)

    else:
        container = cmds.container(current=True)

    try:
        yield container

    finally:
        cmds.container(edit=True, current=current if current else 0)
