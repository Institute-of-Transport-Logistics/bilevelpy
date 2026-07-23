# Datasets — EntityStore & MultiEntityDataset

BilevelPy stores data in named **entity stores**, each mapping tuples to scalar values. Models, solvers, and benchmarks all read data through these stores.

## EntityStore

An `EntityStore` maps **tuples to a scalar value** — like a sparse multi-dimensional array with labeled dimensions.

```python
from bilevelpy.data.core import EntityStore

# Create a 2D cost matrix: (i, j) → cost
costs = EntityStore(
    name="c",
    keys=["fromnode", "tonode"],
    data_map={
        (1, 1): 0.0,
        (1, 2): 4.5,
        (2, 1): 4.5,
        (2, 2): 0.0,
    },
)
```

### Core Operations

```python
# O(1) tuple lookup
value = costs[1,2]    # Result: 4.5
value = costs(2)         # Result: {(2, 1): 4.5, (2, 2): 0.0}

# Iteration
for (i, j), cost in costs.items():
    print(f"Cost from {i} to {j}: {cost}")

# All values
all_costs = list(costs.values)  # [0.0, 4.5, 4.5, 0.0]

# Convert to DataFrame
df = costs.to_dataframe()
#    fromnode tonode    c
# 0         1      1  0.0
# 1         1      2  4.5
# 2         2      1  4.5
# 3         2      2  0.0

# Find all keys mapping to a specific value
zero_cost_routes = costs.find_by_value(0.0)  # [(1, 1), (2, 2)]
```

### Updating Data

```python
# Replace all data
costs.set_data({(1, 3): 7.2, (3, 1): 7.2})
```

### Validation

EntityStore enforces consistency:

```python
# ❌ Keys must be tuples, not scalars
costs.set_data({1: 5.0})  # TypeError

# ❌ All keys must match the declared number of dimensions
costs.set_data({("1",): 5.0})  # ValueError (expects 2 dimensions)
```

## MultiEntityDataset

A `MultiEntityDataset` is a container of named `EntityStore` instances, keyed by `DataCol` identifiers.

```python
from bilevelpy.data.core import MultiEntityDataset
from bilevelpy.core.columns import DataCol

dataset = MultiEntityDataset()

# Add named entities
dataset.add_entity(
    name=DataCol.COST_NODE_TO_NODE,
    keys=[DataCol.START_NODE, DataCol.END_NODE],
    data_map={(1, 2): 4.5, (2, 1): 4.5},
)

dataset.add_entity(
    name=DataCol.NODE_ID,
    keys=[DataCol.NODE_ID],
    data_map={(1,): 1, (2,): 2},
)

# Access by DataCol enum
cost_entity = dataset[DataCol.COST_NODE_TO_NODE]
node_entity = dataset[DataCol.NODE_ID]

# Check membership
has_costs = DataCol.COST_NODE_TO_NODE in dataset  # True

# Iterate all entities
for name in dataset:
    print(f"Entity: {name}")
```

### Merging Datasets

```python
# Combine two datasets with +
merged = dataset_a + dataset_b
```

## The DatasetBuilder Pipeline

`DatasetBuilder` chains processors that transform the dataset incrementally:

```python
from bilevelpy.core.datasets import Dataset
from bilevelpy.data.builder import DatasetBuilder
from bilevelpy.data.loaders import HLPLoader
from bilevelpy.data.processor import HLPNodeSelector, HLPCostScaling

dataset = (
    DatasetBuilder()
    .pipe(HLPLoader(Dataset.CAB100))        # Load raw CAB file
    .pipe(HLPNodeSelector(n_nodes=10))       # Keep 10 nodes
    .pipe(HLPCostScaling(scaling_factor=100)) # Scale costs
    .build()                                 # Run the pipeline
)

# Now dataset contains:
#   DataCol.NODE_ID — 10 node IDs
#   DataCol.COST_NODE_TO_NODE — 10×10 cost matrix (scaled)
#   DataCol.WEIGHTS_NODE_TO_NODE — 10×10 weight matrix
```

Each processor is an `EntityProcessor` that receives the dataset and modifies it in-place. Subclass `EntityProcessor` and implement `process(dataset)` to create your own.