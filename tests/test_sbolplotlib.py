import importlib.util
import sys
import types
from pathlib import Path


def load_sbolplotlib():
    dpl_stub = types.ModuleType("dnaplotlib")
    dpl_stub.DNARenderer = object
    sys.modules["dnaplotlib"] = dpl_stub
    spec = importlib.util.spec_from_file_location(
        "sbolplotlib", Path(__file__).parents[1] / "dnaplotlib" / "sbol" / "sbolplotlib.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


SBOLRenderer = load_sbolplotlib().SBOLRenderer


class ReferencedComponent:
    def __init__(self, roles):
        self.roles = roles


class LookupReference:
    def __init__(self, referenced_component):
        self.referenced_component = referenced_component

    def lookup(self):
        return self.referenced_component


class SubComponent:
    def __init__(self, roles=None, instance_of=None, role_integration=None):
        self.roles = roles or []
        self.instance_of = instance_of
        self.role_integration = role_integration


def test_subcomponent_roles_prefers_subcomponent_roles():
    renderer = SBOLRenderer()
    subcomponent = SubComponent(
        roles=["https://identifiers.org/SO:0000167"],
        instance_of=ReferencedComponent(["https://identifiers.org/SO:0000316"]),
    )

    assert renderer._subcomponent_roles(subcomponent) == ["https://identifiers.org/SO:0000167"]


def test_subcomponent_roles_falls_back_to_referenced_component_roles():
    renderer = SBOLRenderer()
    referenced_component = ReferencedComponent(["https://identifiers.org/SO:0000316"])
    subcomponent = SubComponent(instance_of=LookupReference(referenced_component))

    assert renderer._subcomponent_roles(subcomponent) == ["https://identifiers.org/SO:0000316"]


def test_subcomponent_roles_honors_override_roles():
    renderer = SBOLRenderer()
    referenced_component = ReferencedComponent(["https://identifiers.org/SO:0000316"])
    subcomponent = SubComponent(
        instance_of=LookupReference(referenced_component),
        role_integration="http://sbols.org/v3#overrideRoles",
    )

    assert renderer._subcomponent_roles(subcomponent) == []


def test_subcomponent_roles_falls_back_for_merge_roles():
    renderer = SBOLRenderer()
    referenced_component = ReferencedComponent(["https://identifiers.org/SO:0000316"])
    subcomponent = SubComponent(
        instance_of=LookupReference(referenced_component),
        role_integration="http://sbols.org/v3#mergeRoles",
    )

    assert renderer._subcomponent_roles(subcomponent) == ["https://identifiers.org/SO:0000316"]
