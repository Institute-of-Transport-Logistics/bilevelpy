# Naming Conventions

## Variable Symbols

| Paper | Code | Gurobi Name | Description |
|-------|------|-------------|-------------|
| $x_{ik}$ | `x[i,k]` | `"x"` | Hub allocation (binary) |
| $c_{ij}$ | `c[i,j]` | `"c"` | Transport cost between nodes |
| $w_{ij}$ | `w[i,j]` | `"w"` | Demand weight between nodes |

## Data Columns

| Identifier | Paper | Description |
|------------|-------|-------------|
| `DataCol.X` | — | X-coordinate of a node |
| `DataCol.Y` | — | Y-coordinate of a node |
| `DataCol.NODE_ID` | — | Unique node identifier |
| `DataCol.START_NODE` | $i$ | Origin node in a route |
| `DataCol.END_NODE` | $j$ | Destination node in a route |
| `DataCol.COST_NODE_TO_NODE` | $c_{ij}$ | Transport cost between two nodes |
| `DataCol.WEIGHTS_NODE_TO_NODE` | $w_{ij}$ | Demand weight between two nodes |

## Datasets

| Identifier | File | Nodes |
|------------|------|-------|
| `Dataset.CAB25` | `cab25.txt` | 25 |
| `Dataset.CAB100` | `cab100.txt` | 100 |