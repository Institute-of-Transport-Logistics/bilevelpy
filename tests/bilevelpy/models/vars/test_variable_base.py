"""Tests for VariableMeta metaclass and Variable ABC."""

import pytest

from bilevelpy.models.meta import VariableMetaData
from bilevelpy.models.vars.core import Variable, VariableMeta



# Minimal Variable subclasses for testing the metaclass
class VarAlpha(Variable):
    var_metadata = VariableMetaData("a", "Alpha", [])
    build = lambda self, model: None


class VarBeta(Variable):
    var_metadata = VariableMetaData("b", "Beta", [])
    build = lambda self, model: None



# Test of VariableMeta
class TestVariableMeta:

    class TestHashing:
        def test_hash_is_stable(self):
            assert hash(VarAlpha) == hash(VarAlpha)

        def test_hash_delegates_to_metadata(self):
            assert hash(VarAlpha) == hash(VarAlpha.var_metadata)

    class TestEquality:
        def test_equal_to_self(self):
            assert VarAlpha == VarAlpha

        def test_equal_by_metadata_value(self):
            class Dup(Variable):
                var_metadata = VariableMetaData("a", "Alpha", [])
                build = lambda self, model: None
            assert VarAlpha == Dup

        def test_not_equal_different_metadata(self):
            assert VarAlpha != VarBeta

        def test_equal_to_metadata_instance(self):
            assert VarAlpha == VariableMetaData("a", "Alpha", [])

        def test_equal_to_string(self):
            assert VarAlpha == "a"
            assert VarAlpha != "x"

        def test_not_equal_to_arbitrary_object(self):
            assert VarAlpha != 42

    class TestRepresentation:
        def test_str_returns_metadata_value(self):
            assert str(VarAlpha) == "a"

        def test_repr_contains_metadata_value(self):
            assert "a" in repr(VarAlpha)
            assert "Variable" in repr(VarAlpha)



# Tests of Variable ABC
class TestVariable:
    def test_cannot_instantiate_abstract(self):
        with pytest.raises(TypeError):
            Variable()