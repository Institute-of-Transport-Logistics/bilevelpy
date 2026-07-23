# Complete Pipeline — Build a Hub Location Model from Scratch

This guide builds a **single-allocation hub location problem** using the core library.

The complete, runnable code is at `examples/full_pipeline.py`.

## What We're Building

The classical Uncapacitated Hub Location Problem (UHLP):

- Choose $p$ nodes to be hubs
- Assign every node to exactly one hub
- Minimize total transport cost (with inter-hub discount $\alpha$)
- Flow goes: origin → first hub → second hub → destination

## The Code

```python
--8<-- "examples/full_pipeline.py"
```

## What We Built — Summary

| Component | Lines | What it does |
|-----------|-------|-------------|
| `AllocationVariable` | ~15 | Binary $x_{ik}$ over all node pairs |
| `ExactHubsConstraint` | ~12 | $\sum x_{kk} = p$ |
| `SingleAssignmentConstraint` | ~12 | $\sum_k x_{ik} = 1$ |
| `HubLinkConstraint` | ~12 | $x_{ik} \leq x_{kk}$ |
| `HubLocationModel` | ~30 | Orchestrates build phases + objective |
| `dataset` pipeline | ~8 | Load + prepare CAB25 data |
| **Total** | **~90 lines** | Complete working HLP solver |

Variables, constraints, and the objective are independent — you can swap, add, or change
them without touching the rest of the model. Dependencies are checked automatically.