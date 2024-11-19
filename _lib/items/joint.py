
from typing import Union, Optional

from maya import cmds
from maya.api import OpenMaya as om

from rig._lib.context import withContainer
from rig._lib import node


class Joint(node.Node):

    IDENTIFIER = "core.item.joint"
    SUFFIX = {
            "joint": "jnt",
            "inverseParent": "invPar",
            "inverseXform": "invXform",
            "preMultiply": "preMlt",
            "postMultiply": "pstMlt",
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
            jnt = node.Node(dag.createNode("joint"))
            invPar = node.Node(dg.createNode("inverseMatrix"))
            invXform = node.Node(dg.createNode("inverseMatrix"))
            preMlt = node.Node(dg.createNode("multMatrix"))
            pstMlt = node.Node(dg.createNode("multMatrix"))

            preMlt['o'] >> jnt['opm']
            invPar['omat'] >> preMlt['i'][1]
            jnt['wm'][0] >> pstMlt['i'][1]

            preMlt['o'] >> invXform['imat']
            invXform['omat'] >> pstMlt['i'][0]

            if name:
                jnt.name = f"{name}_{cls.SUFFIX['joint']}"
                invPar.name = f"{name}_{cls.SUFFIX['inverseParent']}"
                invXform.name = f"{name}_{cls.SUFFIX['inverseXform']}"
                preMlt.name = f"{name}_{cls.SUFFIX['preMultiply']}"
                pstMlt.name = f"{name}_{cls.SUFFIX['postMultiply']}"

        dag.doIt()
        dg.doIt()

        cmds.container(container, publishAndBind=[str(preMlt['i'][0]), "inp_xform"], edit=True)
        cmds.container(container, publishAndBind=[str(preMlt['i'][1]), "inp_parent"], edit=True)

        cmds.container(container, publishAndBind=[str(pstMlt['o']), "out_output"], edit=True)
        cmds.container(container, publishAndBind=[str(jnt['wm'][0]), "out_worldMatrix"], edit=True)
        cmds.container(container, publishAndBind=[str(jnt['pm'][0]), "out_parentMatrix"], edit=True)
        cmds.container(container, publishAndBind=[str(jnt['m']), "out_matrix"], edit=True)

        cmds.container(container, edit=True, publishAsRoot=[jnt.name, True])
        cmds.setAttr(f"{container}.containerType", cls.IDENTIFIER, typ="string")

        return cls(container)
