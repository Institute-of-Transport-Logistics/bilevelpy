"""Tests for Constraint ABC."""

import pytest

from bilevelpy.models.constraints.core import Constraint


class TestConstraint:
    def test_cannot_instantiate_abstract(self):
        with pytest.raises(TypeError):
            Constraint()

    def test_default_required_vars_is_empty(self):
        assert Constraint.required_vars == []

    def test_concrete_subclass_can_be_instantiated(self):
        class MyConstraint(Constraint):
            def build(self, model, **kwargs):
                pass

        assert MyConstraint() is not None
        assert MyConstraint.required_vars == []