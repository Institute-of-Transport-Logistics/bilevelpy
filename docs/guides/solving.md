# Solving Models

## Basic Solve

```python
from bilevelpy import ModelSolver

solver = ModelSolver(model)
solution = solver.solve()
```

`ModelSolver` configures Gurobi, runs the optimization, extracts variable values,
and returns a `BaseModelSolution`.

## Solver Configuration

Pass parameters at construction time:

```python
solver = ModelSolver(
    model,
    time_limit=300,       # 5 minute limit
    mip_gap=0.01,         # 1% gap tolerance
    use_max_threads=True,  # all cores
)
solution = solver.solve()
```

## Inspecting the Solution

```python
# Solution metadata
print(solution.solution_metadata.objective_value)     # 1234.56
print(solution.solution_metadata.solving_time)        # 2.34 (seconds)
print(solution.solution_metadata.is_optimal)          # True
print(solution.solution_metadata.mip_gap)             # 0.0
print(solution.solution_metadata.node_count)          # 1542

# Access extracted variable values
x = solution.solution_data[AllocationVariable]
y = solution.solution_data[ClientDecisionVariable]

# Each is an EntityStore — all EntityStore operations work:
df_x = x.to_dataframe()
active_hubs = x.find_by_value(1.0)  # list of (i,k) with x[i,k] == 1

# Iterate
for (i, k), val in x.items():
    if val > 0.5:
        print(f"Node {i} assigned to hub {k}")
```

## Merging Solution with Input Data

```python
# Combine solution variables with the original input data
merged = solution.solution_data + model.data
# Now merged contains both solution variables and input data
```

## Solution String Representation

Call `print(solution)` for a formatted summary:

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

## Memory Management

```python
# Release the Gurobi model (frees memory)
solution.dispose()
```

## Error Handling

```python
try:
    solution = ModelSolver(model).solve()
    if not solution.solution_metadata.is_optimal:
        print(f"Suboptimal solution with gap {solution.solution_metadata.mip_gap}")
except Exception as e:
    print(f"Solver failed: {e}")
```

## The Solution Registry

When you decorate a model with `@SolutionRegistry.register_for(...)`, the solver automatically finds the correct solution class:

```python
from bilevelpy.solution import SolutionRegistry
from bilevelpy.solution.core import BaseModelSolution

class MyCustomSolution(BaseModelSolution):
    """Custom solution with extra post-processing."""
    ...

@SolutionRegistry.register_for(MyCustomSolution)
class MyModel(BaseModel):
    ...

# When ModelSolver runs, it calls SolutionRegistry.get_solution_class(model)
# → finds MyCustomSolution → instantiates it → returns
```