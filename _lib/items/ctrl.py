from typing import Union, Optional

from maya import cmds
from maya.api import OpenMaya as om

from rig._lib.context import withContainer
from rig._lib import node


class Ctrl(node.Node):

    IDENTIFIER = "core.item.ctrl"
    SUFFIX = {
            "control": "ctrl",
            "preMatrix": "preMat",
            "postMatrix": "pstMat",
            "inverseMatrix": "invMat",
            "container": "ast"
            }

    @classmethod
    def create(
            cls,
            name: Optional[str] = None,
            module=Optional[Union[om.MObject, str]]
            ) -> node.Node:

        dag = om.MDagModifier()
        dg = om.MDGModifier()

        with withContainer(cls.SUFFIX.get("container", "ast")) as container:
            ctrl = node.Node(dag.createNode("transform"))
            invMat = node.Node(dg.createNode("inverseMatrix"))
            preMlt = node.Node(dg.createNode("multMatrix"))
            pstMlt = node.Node(dg.createNode("multMatrix"))

            preMlt['o'] >> ctrl['opm']
            preMlt['i'][0] >> invMat['imat']
            invMat['omat'] >> pstMlt['i'][0]
            ctrl['wm'][0] >> pstMlt['i'][1]

            if name:
                ctrl.name = f"{name}_{cls.SUFFIX['control']}"
                invMat.name = f"{name}_{cls.SUFFIX['inverseMatrix']}"
                pstMlt.name = f"{name}_{cls.SUFFIX['postMatrix']}"
                preMlt.name = f"{name}_{cls.SUFFIX['preMatrix']}"

        dag.doIt()
        dg.doIt()

        cmds.container(container, edit=True,
                       publishAndBind=[str(preMlt['i'][0]), "inp_xform"])

        cmds.container(container, edit=True,
                       publishAndBind=[str(preMlt['i'][1]), "inp_input"])

        cmds.container(container, edit=True,
                       publishAndBind=[str(pstMlt['o']), "out_output"])

        cmds.container(container, edit=True,
                       publishAndBind=[str(ctrl['wm'][0]), "out_worldMatrix"])

        cmds.container(container, edit=True,
                       publishAndBind=[str(ctrl['pm'][0]), "out_parentMatrix"])

        cmds.container(container, edit=True,
                       publishAndBind=[str(ctrl['m']), "out_matrix"])

        cmds.container(container, edit=True, publishAsRoot=[ctrl.name, True])
        cmds.setAttr(f"{container}.containerType", cls.IDENTIFIER, typ="string")

        return cls(container)
