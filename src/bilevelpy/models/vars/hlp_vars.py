from gurobipy import GRB, tupledict

from bilevelpy.core.columns import DataCol
from bilevelpy.models.meta import VariableMetaData
from bilevelpy.models.utils import get_nodes
from bilevelpy.models.vars.core import Variable


class AllocationVariable(Variable):
    r"""Binary hub allocation variable for the Hub Location Problem.

    $$x_{ik} \in \{0,1\} \quad \forall i,k \in V$$

    $x_{ik} = 1$ means node $i$ is assigned to hub $k$. The special case
    $x_{kk} = 1$ means node $k$ is open as a hub.

    Identifiers: ``(i, k)`` where $i,k \in V$.
    """

    var_metadata = VariableMetaData(
        value="x",
        display_name="Allocations",
        identifiers=[DataCol.START_NODE, DataCol.END_NODE],
    )

    def build(self, model: "BaseModel") -> tupledict:
        """Create $|V| \times |V|$ binary Gurobi variables."""
        nodes = get_nodes(model)
        return model.model.addVars(
            nodes, nodes,
            vtype=GRB.BINARY,
            name=str(self.var_metadata),
        )

    def validate(self, model: "BaseModel") -> None:
        """No additional validation needed."""
        pass