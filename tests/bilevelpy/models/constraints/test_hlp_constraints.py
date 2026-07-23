"""Tests for HLP constraint classes."""

from bilevelpy.models.constraints.core import Constraint
from bilevelpy.models.constraints.hlp_constraints import (
    NumberOfHubsConstraint,
    SingleAllocationConstraint,
    AssignmentRestrictionConstraint,
)
from bilevelpy.models.vars.hlp_vars import AllocationVariable


class TestNumberOfHubsConstraint:
    def test_is_constraint_subclass(self):
        assert issubclass(NumberOfHubsConstraint, Constraint)

    def test_required_vars(self):
        assert NumberOfHubsConstraint.required_vars == [AllocationVariable]

    def test_can_instantiate(self):
        assert NumberOfHubsConstraint() is not None


class TestSingleAllocationConstraint:
    def test_is_constraint_subclass(self):
        assert issubclass(SingleAllocationConstraint, Constraint)

    def test_required_vars(self):
        assert SingleAllocationConstraint.required_vars == [AllocationVariable]

    def test_can_instantiate(self):
        assert SingleAllocationConstraint() is not None


class TestAssignmentRestrictionConstraint:
    def test_is_constraint_subclass(self):
        assert issubclass(AssignmentRestrictionConstraint, Constraint)

    def test_required_vars(self):
        assert AssignmentRestrictionConstraint.required_vars == [AllocationVariable]

    def test_can_instantiate(self):
        assert AssignmentRestrictionConstraint() is not None