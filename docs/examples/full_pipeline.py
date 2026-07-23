"""Complete Pipeline: Building a Hub Location Model from Scratch.

Runnable example: single-allocation uncapacitated hub location problem
built with the core library.

"""

from gurobipy import GRB, quicksum

from bilevelpy import (
    BaseModel, BaseModelSolution, Constraint, DataCol,
    Dataset, ModelMetaData, ModelSolver, SolutionRegistry,
    Variable, VariableMetaData,
)
from bilevelpy.data.builder import DatasetBuilder
from bilevelpy.data.loaders import HLPLoader
from bilevelpy.data.processor import HLPNodeSelector, HLPCostScaling

# ---------------------------------------------------------------------------
# Step 1: Load and prepare data
# ---------------------------------------------------------------------------

dataset = (
    DatasetBuilder()
    .pipe(HLPLoader(Dataset.CAB25)) # we load the CAB25 Dataset
    .pipe(HLPNodeSelector(n_nodes=10)) # we select 10 nodes from the dataset
    .pipe(HLPCostScaling(scaling_factor=100)) # divide costs by 100
    .build()
)

nodes = list(dataset[DataCol.NODE_ID].values)
print(f"Nodes: {nodes}")


# ---------------------------------------------------------------------------
# Step 2: Variable — binary x[i,k] for hub allocation
# ---------------------------------------------------------------------------

class AllocationVariable(Variable):
    r"""Binary: $x_{ik} = 1$ if node $i$ assigned to hub $k$.

    $x_{kk} = 1$ means node $k$ is open as a hub.
    """

    var_metadata = VariableMetaData(
        value="x",
        display_name="Hub Allocation",
        identifiers=[DataCol.START_NODE, DataCol.END_NODE],
    )

    def build(self, model: "BaseModel"):
        nodes = list(model.data[DataCol.NODE_ID].values)
        return model.model.addVars(nodes, nodes, vtype=GRB.BINARY, name="x")


# ---------------------------------------------------------------------------
# Step 3: Constraints
# ---------------------------------------------------------------------------

class ExactHubsConstraint(Constraint):
    r"""Exactly $p$ hubs: $\sum_{k \in V} x_{kk} = p$."""

    required_vars = [AllocationVariable]

    def build(self, model: "BaseModel", **kwargs):
        n_hubs = kwargs["n_hubs"]
        nodes = list(model.data[DataCol.NODE_ID].values)
        x = model.vars[AllocationVariable]
        model.add_constr(
            quicksum(x[k, k] for k in nodes) == n_hubs, name="exact_hubs"
        )


class SingleAssignmentConstraint(Constraint):
    r"""Every node to exactly one hub: $\sum_k x_{ik} = 1$."""

    required_vars = [AllocationVariable]

    def build(self, model: "BaseModel", **kwargs):
        nodes = list(model.data[DataCol.NODE_ID].values)
        x = model.vars[AllocationVariable]
        for i in nodes:
            model.add_constr(
                quicksum(x[i, k] for k in nodes) == 1, name=f"assign_{i}"
            )


class HubLinkConstraint(Constraint):
    r"""Can only assign to open hubs: $x_{ik} \leq x_{kk}$."""

    required_vars = [AllocationVariable]

    def build(self, model: "BaseModel", **kwargs):
        nodes = list(model.data[DataCol.NODE_ID].values)
        x = model.vars[AllocationVariable]
        for i in nodes:
            for k in nodes:
                model.add_constr(x[i, k] <= x[k, k], name=f"link_{i}_{k}")


# ---------------------------------------------------------------------------
# Step 4: Model — quadratic objective with inter-hub discount α
# ---------------------------------------------------------------------------

@SolutionRegistry.register_for(BaseModelSolution)
class HubLocationModel(BaseModel):
    """Single-allocation uncapacitated hub location problem."""

    model_metadata = ModelMetaData(value="UHLP", display_name="Uncapacitated HLP")

    def __init__(self, n_hubs: int, alpha: float, data):
        super().__init__(data)
        self._n_hubs = n_hubs
        self._alpha = alpha
        self.build(
            variables=[AllocationVariable],
            constraints=[
                ExactHubsConstraint,
                SingleAssignmentConstraint,
                HubLinkConstraint,
            ],
            n_hubs=n_hubs,
        )

    def _set_objective(self, **kwargs):
        r"""Minimize $\sum w_{ij} x_{ik} x_{jm} (c_{ik} + \alpha c_{km} + c_{mj})$."""
        costs = self.data[DataCol.COST_NODE_TO_NODE]
        weights = self.data[DataCol.WEIGHTS_NODE_TO_NODE]
        nodes = list(self.data[DataCol.NODE_ID].values)
        x = self.vars[AllocationVariable]

        obj = quicksum(
            weights[i, j]
            * x[i, k]
            * x[j, m]
            * (costs[i, k] + self._alpha * costs[k, m] + costs[m, j])
            for i in nodes
            for j in nodes
            for k in nodes
            for m in nodes
        )
        return obj, GRB.MINIMIZE


# ---------------------------------------------------------------------------
# Step 5: Solve and inspect
# ---------------------------------------------------------------------------

model = HubLocationModel(n_hubs=3, alpha=0.5, data=dataset)
solution = ModelSolver(model).solve()

print(f"Objective: {solution.solution_metadata.objective_value:.2f}")
print(f"Time: {solution.solution_metadata.solving_time:.2f}s")
print(f"Optimal: {solution.solution_metadata.is_optimal}")

x = solution.solution_data[AllocationVariable]
open_hubs = [k for (i, k), val in x.items() if i == k and val > 0.5]
print(f"Open hubs: {open_hubs}")

for (i, k), val in x.items():
    if val > 0.5 and i != k:
        print(f"  Node {i} → Hub {k}")