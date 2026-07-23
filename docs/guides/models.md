# Models — Variables, Constraints & BaseModel

BilevelPy models are built from three parts: **Variables**, **Constraints**, and a **BaseModel** subclass.

## Custom Variables

Every variable extends [`Variable`][bilevelpy.models.vars.core.Variable] and declares its
[`VariableMetaData`][bilevelpy.models.meta.VariableMetaData] — a short code, a display name,
and the dimensions (list of [`DataCol`][bilevelpy.core.columns.DataCol] entries) the variable
spans. The abstract [`build()`][bilevelpy.models.vars.core.Variable.build] method returns a
Gurobi `tupledict`.

```python
from bilevelpy import Variable, VariableMetaData, DataCol

class AssignmentVar(Variable):
    var_metadata = VariableMetaData(
        value="x",
        display_name="Hub Assignments",
        identifiers=[DataCol.START_NODE, DataCol.END_NODE],
    )

    def build(self, model):
        nodes = list(model.data[DataCol.NODE_ID].values)
        return model.model.addVars(nodes, nodes, vtype="B", name="x")
```

Constraints declare dependencies via `required_vars` so the framework can validate
the build order:

```python
from bilevelpy import Constraint

class ExactHubs(Constraint):
    required_vars = [AssignmentVar]

    def build(self, model, **kwargs):
        n_hubs = kwargs["n_hubs"]
        nodes = list(model.data[DataCol.NODE_ID].values)
        x = model.vars[AssignmentVar]
        model.add_constr(sum(x[k, k] for k in nodes) == n_hubs, name="exact_hubs")
```

See the [Full Pipeline example](full_pipeline.md) for a complete runnable model.

## The Build Phases in Detail

`BaseModel.build()` runs four phases:

1. **Variables** — each `Variable.build()` creates Gurobi variables. Results stored in `self.vars[VarClass]`.
2. **Validate** — checks that every constraint's `required_vars` exist in `self.vars`. Missing deps raise `ValueError`.
3. **Constraints** — each `Constraint.build()` adds Gurobi constraints (the variables are already built).
4. **Objective** — `_set_objective()` is called. If it returns `(expression, sense)`, `model.setObjective()` is called.

Constraints can access `model.vars[VarClass]` — the variable always exists before the constraint runs.

## Dependency Validation

```python
class BadConstraint(Constraint):
    required_vars = [SomeVariable]  # not in the variables list
    def build(self, model, **kwargs):
        pass

model.build(variables=[AllocationVariable], constraints=[BadConstraint])
# → ValueError: BadConstraint requires variables
#   [<class 'SomeVariable'>] that were not built.
#   Add them to the 'variables' list.
```

Dependency errors surface during `build()`, not halfway through an optimization run.
