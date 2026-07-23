# <img src="resources/bilevelpy_logo_text_no_background.png" alt="BilevelPy" height="32">



An extensible Python framework for building, solving, and evaluating **[Gurobi](https://www.gurobi.com/)-based optimization models**, with built-in support for hub-location problems.
## What BilevelPy Provides

| Component | Description |
|-----------|-------------|
| **Model Building** | Build Gurobi models from `Variable` and `Constraint` classes |
| **Preloaded Datasets** | CAB25, CAB100, and other benchmark instances via `HLPLoader(Dataset.CAB100)` |
| **Preprocessors** | Built-in filters, selectors, and cost scalers (`HLPNodeSelector`, `HLPCostScaling`, …) |
| **Data Pipeline** | Chain loaders and preprocessors with `DatasetBuilder` |
| **Solving** | Configure and run Gurobi with automatic solution extraction |
| **Benchmarking** | Compare models across scenarios with structured logging and reporting |

## Quick Example — Hub Location Problem

For a thorough pipeline example, see the [Full Pipeline Example](guides/full_pipeline.md).

```python
from gurobipy import GRB, quicksum

from bilevelpy import (
    BaseModel, BaseModelSolution, DataCol, Dataset,
    ModelSolver, SolutionRegistry,
)
from bilevelpy.data.builder import DatasetBuilder
from bilevelpy.data.loaders import HLPLoader
from bilevelpy.data.processor import HLPNodeSelector, HLPCostScaling
from bilevelpy.models.constraints import (
    AssignmentRestrictionConstraint,
    NumberOfHubsConstraint,
    SingleAllocationConstraint,
)
from bilevelpy.models.vars import AllocationVariable


@SolutionRegistry.register_for(BaseModelSolution)
# Build the mathematical model
class MyHLP(BaseModel):
    def __init__(self, n_hubs, data):
        super().__init__(data)
        self.build(
            variables=[AllocationVariable],
            constraints=[
                NumberOfHubsConstraint,
                SingleAllocationConstraint,
                AssignmentRestrictionConstraint,
            ],
            n_hubs=n_hubs,
        )

    def _set_objective(self, **kwargs):
        """Minimize total transport cost with inter-hub discount α."""
        costs = self.data[DataCol.COST_NODE_TO_NODE]
        weights = self.data[DataCol.WEIGHTS_NODE_TO_NODE]
        nodes = list(self.data[DataCol.NODE_ID].values)
        x = self.vars[AllocationVariable]
        alpha = 0.5  # inter-hub discount factor

        obj = quicksum(
            weights[i, j]
            * x[i, k]
            * x[j, m]
            * (costs[i, k] + alpha * costs[k, m] + costs[m, j])
            for i in nodes
            for j in nodes
            for k in nodes
            for m in nodes
        )
        return obj, GRB.MINIMIZE


# 1. Build dataset
dataset = (
    DatasetBuilder()
    .pipe(HLPLoader(Dataset.CAB100))
    .pipe(HLPNodeSelector(n_nodes=10))
    .pipe(HLPCostScaling(scaling_factor=100))
    .build()
)

# 2. Create and solve
model = MyHLP(n_hubs=2, data=dataset)
solution = ModelSolver(model).solve()
print(solution)
```