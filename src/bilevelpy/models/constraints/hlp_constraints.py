from __future__ import annotations

from typing import TYPE_CHECKING

from gurobipy import quicksum

from bilevelpy.models.constraints.core import Constraint
from bilevelpy.models.utils import get_nodes
from bilevelpy.models.vars.hlp_vars import AllocationVariable

if TYPE_CHECKING:
    from bilevelpy.models.core import BaseModel


class NumberOfHubsConstraint(Constraint):
    r"""Fix the number of open hubs to exactly $p$.

    $$\sum_{j \in V} x_{jj} = p$$

    Requires:
        [AllocationVariable][bilevelpy.models.vars.hlp_vars.AllocationVariable]
    """

    required_vars = [AllocationVariable]

    def build(self, model: BaseModel, **kwargs):
        """Add the hub count constraint.

        Args:
            model: The [BaseModel][bilevelpy.models.core.BaseModel] instance.
            **kwargs: Must contain ``n_hubs`` (``int``).
        """
        n_hubs = kwargs["n_hubs"]
        nodes = get_nodes(model)
        x = model.vars[AllocationVariable]
        model.add_constr(
            quicksum(x[j, j] for j in nodes) == n_hubs,
            name="hub_count",
        )


class SingleAllocationConstraint(Constraint):
    r"""Ensure each node is assigned to exactly one hub.

    $$\sum_{j \in V} x_{ij} = 1 \quad \forall i \in V$$

    Requires:
        [AllocationVariable][bilevelpy.models.vars.hlp_vars.AllocationVariable]
    """

    required_vars = [AllocationVariable]

    def build(self, model: BaseModel, **kwargs):
        """Add single-allocation constraints for all nodes.

        Args:
            model: The [BaseModel][bilevelpy.models.core.BaseModel] instance.
            **kwargs: Not used (present for interface consistency).
        """
        nodes = get_nodes(model)
        x = model.vars[AllocationVariable]
        for i in nodes:
            model.add_constr(
                quicksum(x[i, j] for j in nodes) == 1,
                name=f"single_assign_{i}",
            )


class AssignmentRestrictionConstraint(Constraint):
    r"""Restrict assignments to open hubs only.

    $$x_{ij} \leq x_{jj} \quad \forall i,j \in V$$

    Requires:
        [AllocationVariable][bilevelpy.models.vars.hlp_vars.AllocationVariable]
    """

    required_vars = [AllocationVariable]

    def build(self, model: BaseModel, **kwargs):
        """Add assignment restriction constraints for all node pairs.

        Args:
            model: The [BaseModel][bilevelpy.models.core.BaseModel] instance.
            **kwargs: Not used (present for interface consistency).
        """
        nodes = get_nodes(model)
        x = model.vars[AllocationVariable]
        for i in nodes:
            for j in nodes:
                model.add_constr(
                    x[i, j] <= x[j, j],
                    name=f"link_{i}_{j}",
                )