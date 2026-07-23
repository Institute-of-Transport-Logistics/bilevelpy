# Quickstart Tutorial

Build and solve a hub location problem from scratch — the same example shown on
the [home page](index.md).

---

## 1. Load a Dataset

BilevelPy ships with preloaded benchmark instances.  Here we load **CAB100**,
keep the first 10 nodes, and divide costs by 100.

```python
from bilevelpy import Dataset
from bilevelpy.data.builder import DatasetBuilder
from bilevelpy.data.loaders import HLPLoader
from bilevelpy.data.processor import HLPNodeSelector, HLPCostScaling

dataset = (
    DatasetBuilder()
    .pipe(HLPLoader(Dataset.CAB100))       # built-in CAB benchmark
    .pipe(HLPNodeSelector(n_nodes=10))     # subset of nodes
    .pipe(HLPCostScaling(scaling_factor=100))
    .build()
)
```

| Method | What it does |
|--------|-------------|
| `HLPLoader(Dataset.CAB100)` | Loads the 100-node CAB dataset from disk |
| `HLPNodeSelector(n_nodes=10)` | Filters to the first 10 nodes for a smaller problem |
| `HLPCostScaling(…)` | Divides costs by the scaling factor |

---

## 2. Build a Model

BilevelPy models are assembled from three building blocks:

- **Variables** — decision variables (e.g. "which hub is node *i* assigned to?")
- **Constraints** — mathematical rules linking those variables
- **Objective** — what to minimise or maximise

### 2a. Declare variables and constraints

`BaseModel.build()` takes a list of `Variable` and `Constraint` **classes**,
not instances. It creates them, validates dependencies, and runs the build
phases in order.

```python
from gurobipy import GRB, quicksum

from bilevelpy import (
    BaseModel, BaseModelSolution, DataCol,
    SolutionRegistry,
)
from bilevelpy.models.constraints import (
    AssignmentRestrictionConstraint,
    NumberOfHubsConstraint,
    SingleAllocationConstraint,
)
from bilevelpy.models.vars import AllocationVariable


@SolutionRegistry.register_for(BaseModelSolution)
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
```

| Class | What it enforces |
|-------|-----------------|
| `AllocationVariable` | Binary $x_{ik}$ — node $i$ assigned to hub $k$ |
| `NumberOfHubsConstraint` | Exactly $p$ hubs: $\sum_k x_{kk} = p$ |
| `SingleAllocationConstraint` | Every node assigned to exactly one hub |
| `AssignmentRestrictionConstraint` | Can only assign to open hubs: $x_{ik} \le x_{kk}$ |

### 2b. Define the objective

Override `_set_objective()` to tell the model *what* to optimise.  Here we minimise
total transport cost with an inter-hub discount factor $\alpha$:

$$\min \sum_{i,j,k,m} w_{ij} \, x_{ik} \, x_{jm} \, (c_{ik} + \alpha \, c_{km} + c_{mj})$$

```python
    def _set_objective(self, **kwargs):
        costs   = self.data[DataCol.COST_NODE_TO_NODE]
        weights = self.data[DataCol.WEIGHTS_NODE_TO_NODE]
        nodes   = list(self.data[DataCol.NODE_ID].values)
        x       = self.vars[AllocationVariable]
        alpha   = 0.5

        obj = quicksum(
            weights[i, j]
            * x[i, k] * x[j, m]
            * (costs[i, k] + alpha * costs[k, m] + costs[m, j])
            for i in nodes for j in nodes
            for k in nodes for m in nodes
        )
        return obj, GRB.MINIMIZE
```

!!! tip "Key point"
    `self.vars[AllocationVariable]` returns the Gurobi tupledict that was built
    during the variable phase.  `self.data[DataCol.…]` accesses the dataset columns
    by name — no magic strings.

---

## 3. Solve

`ModelSolver` configures Gurobi and runs the optimization. Call `.solve()` to
get a typed solution object back.

```python
from bilevelpy import ModelSolver

model = MyHLP(n_hubs=2, data=dataset)
solution = ModelSolver(model).solve()

# Quick summary
print(f"Objective: {solution.solution_metadata.objective_value:.2f}")
print(f"Time:      {solution.solution_metadata.solving_time:.2f}s")
print(f"Optimal:   {solution.solution_metadata.is_optimal}")
```

For a full breakdown, call `print(solution)`:

```
==================================================
SOLUTION SUMMARY: Uncapacitated HLP
==================================================
Variables Extracted : Allocations
--------------------------------------------------
Gurobi Configuration:
  Threads     : 1
  IntFeasTol  : 1e-09
--------------------------------------------------
Solution Metadata:
  Solving Time (s)  : 0.007
  Objective Value   : 3875.96
  Is Optimal        : True
  MIP Gap (%)       : 0.0
  Nodes Explored    : 1
==================================================
```

---

## 4. Inspect Results

The solution object stores variable values keyed by the `Variable` class.
Call `.to_dataframe()` for a clean tabular view:

```python
x = solution.solution_data[AllocationVariable]
print(x.to_dataframe())
```

```
   fromnode  tonode    x
0         0       0  1.0
1         0       1  0.0
2         0       2  0.0
3         1       0  1.0
4         1       1  0.0
5         1       2  0.0
6         2       0  0.0
7         2       1  0.0
8         2       2  1.0
```

---

## Next Steps

- [Full Pipeline Example](guides/full_pipeline.md) — build custom variables and
  constraints yourself
- [Build Datasets](guides/datasets.md) — learn the full data pipeline
- [Build Models](guides/models.md) — dive deeper into variables, constraints,
  and the build lifecycle