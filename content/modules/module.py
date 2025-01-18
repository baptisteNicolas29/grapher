from maya import cmds
from maya.api import OpenMaya as om

from rig._lib import node
from rig._lib.context import withContainer


class Module(node.Node):

    IDENTIFIER = "core.module.void"

    SUFFIX = {
            "container": "ast",
            }

    @classmethod
    def create(cls) -> None:

        mod = om.MDagModifier()

        with withContainer(cls.SUFFIX.get("container", "ast")) as container:
            grp = node.Node(mod.createNode("transform"))

            mod.renameNode(grp, "grp")
            grp['it'].setBool(False)

            sub_nodes = {}
            for name, (longname, color) in {
                'inp': ["input", [.5, .5, 1.]],
                'out': ["output", [.5, .5, 1.]],
                'pbl': ["public", [.5, 1., .5]],
                'inter': ["interface", [.5, 1., .5]],
                'pri': ["private", [1., .5, .5]],
                'conf': ["config", [1., .5, .5]],
            }.items():

                prop = node.Node(mod.createNode("transform", grp))
                prop.name = name
                prop['it'].setBool(False)
                prop['uocol'].setBool(True)
                prop['oclrr'].setDouble(color[0])
                prop['oclrg'].setDouble(color[1])
                prop['oclrb'].setDouble(color[2])

                attr = om.MFnMessageAttribute().create(longname, name)
                om.MFnDependencyNode(grp).addAttribute(attr)
                prop['msg'] >> grp[name]
                sub_nodes[name] = prop

            mod.reparentNode(sub_nodes['inter'], sub_nodes['pbl'])
            mod.reparentNode(sub_nodes['conf'], sub_nodes['pri'])

        mod.doIt()
        cmds.container(container, edit=True, publishAsRoot=[grp.name, True])
        cmds.setAttr(f"{container}.containerType", cls.IDENTIFIER, typ="string")

        return cls(grp)

    def _get_property(self, property_name: str) -> None:
        src = self[property_name].source()
        return node.Node(src.node())

    @property
    def input(self):
        """The input property."""
        return self._get_property('inp')

    @property
    def output(self):
        """The input property."""
        return self._get_property('out')

    @property
    def public(self):
        """The input property."""
        return self._get_property('pbl')

    @property
    def private(self):
        """The input property."""
        return self._get_property('pri')

    @property
    def interface(self):
        """The input property."""
        return self._get_property('inter')

    @property
    def config(self):
        """The input property."""
        return self._get_property('conf')
