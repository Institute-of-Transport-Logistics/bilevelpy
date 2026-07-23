"""Tests for AllocationVariable."""

from bilevelpy.core.columns import DataCol
from bilevelpy.models.meta import VariableMetaData
from bilevelpy.models.vars.core import Variable
from bilevelpy.models.vars.hlp_vars import AllocationVariable


class TestAllocationVariable:

    class TestMetadata:
        def test_value_is_x(self):
            assert AllocationVariable.var_metadata.value == "x"

        def test_display_name(self):
            assert AllocationVariable.var_metadata.display_name == "Allocations"

        def test_identifiers(self):
            assert AllocationVariable.var_metadata.identifiers == [
                DataCol.START_NODE,
                DataCol.END_NODE,
            ]

    class TestVariableProtocol:
        def test_is_variable_subclass(self):
            assert issubclass(AllocationVariable, Variable)

        def test_can_instantiate(self):
            # AllocationVariable is concrete (has build, var_metadata)
            assert AllocationVariable() is not None

        def test_hashable(self):
            d = {AllocationVariable: "x"}
            assert d[AllocationVariable] == "x"