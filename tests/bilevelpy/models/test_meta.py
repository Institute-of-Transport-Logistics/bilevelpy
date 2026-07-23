"""Tests for VariableMetaData and ModelMetaData."""

from bilevelpy.core.columns import DataCol
from bilevelpy.models.meta import VariableMetaData, ModelMetaData
from bilevelpy.models.vars.core import Variable



# Tests of VariableMetaData
class TestVariableMetaData:

    class TestConstruction:
        def test_stores_fields(self):
            meta = VariableMetaData("x", "Allocations", [DataCol.START_NODE, DataCol.END_NODE])
            assert meta.value == "x"
            assert meta.display_name == "Allocations"
            assert meta.identifiers == [DataCol.START_NODE, DataCol.END_NODE]

        def test_default_description_is_empty(self):
            meta = VariableMetaData("x", "X", [])
            assert meta.description == ""

        def test_number_of_identifiers(self):
            meta = VariableMetaData("y", "Y", [DataCol.START_NODE, DataCol.END_NODE])
            assert meta.number_of_identifiers == 2

    class TestEquality:
        def test_equal_by_value(self):
            a = VariableMetaData("x", "Alpha", [])
            b = VariableMetaData("x", "Beta", [DataCol.NODE_ID])
            assert a == b

        def test_not_equal_different_value(self):
            assert VariableMetaData("x", "X", []) != VariableMetaData("y", "Y", [])

        def test_equal_to_string(self):
            assert VariableMetaData("x", "X", []) == "x"

        def test_not_equal_to_string(self):
            assert VariableMetaData("x", "X", []) != "y"

        def test_equal_to_variable_class(self):
            class VarX(Variable):
                var_metadata = VariableMetaData("x", "X", [])
                build = lambda self, model: None
            assert VariableMetaData("x", "X", []) == VarX

    class TestHashing:
        def test_hash_by_value(self):
            assert hash(VariableMetaData("x", "A", [])) == hash(VariableMetaData("x", "B", [DataCol.NODE_ID]))

    class TestRepresentation:
        def test_str_returns_value(self):
            assert str(VariableMetaData("x", "Allocations", [])) == "x"

        def test_repr_contains_value(self):
            assert "x" in repr(VariableMetaData("x", "Allocations", []))



# Tests of ModelMetaData
class TestModelMetaData:

    class TestConstruction:
        def test_stores_fields(self):
            meta = ModelMetaData("UHLP", "Uncapacitated HLP")
            assert meta.value == "UHLP"
            assert meta.display_name == "Uncapacitated HLP"

    class TestEquality:
        def test_equal_by_value(self):
            assert ModelMetaData("A", "Foo") == ModelMetaData("A", "Bar")

        def test_not_equal_different_value(self):
            assert ModelMetaData("A", "Foo") != ModelMetaData("B", "Foo")

        def test_equal_to_string(self):
            assert ModelMetaData("A", "Foo") == "A"

        def test_not_equal_to_string(self):
            assert ModelMetaData("A", "Foo") != "B"

    class TestHashing:
        def test_hash_by_value(self):
            assert hash(ModelMetaData("A", "Foo")) == hash(ModelMetaData("A", "Bar"))

    class TestRepresentation:
        def test_str_returns_display_name(self):
            assert str(ModelMetaData("UHLP", "Uncapacitated HLP")) == "Uncapacitated HLP"

        def test_repr_contains_value(self):
            assert "UHLP" in repr(ModelMetaData("UHLP", "Uncapacitated HLP"))