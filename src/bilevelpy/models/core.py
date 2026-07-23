from typing import Any

from gurobipy import Constr, Model

from bilevelpy.data.core import MultiEntityDataset
from bilevelpy.models.meta import ModelMetaData
from bilevelpy.models.vars.core import Variable
from bilevelpy.models.constraints.core import Constraint


class BaseModel:
    r"""Base class for building optimization models from variables and constraints.

    Models are assembled by declaring which
    [`Variable`][bilevelpy.models.vars.core.Variable] subclasses and
    [`Constraint`][bilevelpy.models.constraints.core.Constraint]
    subclasses to apply.

    **Build phases:**

    1. **Variables** — each ``Variable`` subclass is instantiated and its
       ``build()`` method is called. The returned Gurobi ``tupledict`` is
       stored in ``self.vars`` keyed by the subclass.
    2. **Validate** — each ``Constraint`` checks that its
       ``required_vars`` are present in ``self.vars``.
    3. **Constraints** — each ``Constraint.build()`` adds Gurobi
       constraints.
    4. **Objective** — ``_set_objective()`` is called. If it returns
       ``(expr, sense)``, the model objective is set.

    Attributes:
        model: The underlying Gurobi ``Model`` instance.
        data: The input dataset.
        vars: Mapping from ``Variable`` subclass to Gurobi ``tupledict``.
        added_vars: Ordered list of ``Variable`` subclasses that were built.
        added_constraints: Ordered list of ``Constraint`` subclasses
            that were applied.
    """

    model_metadata: ModelMetaData

    def __init__(self, data: MultiEntityDataset) -> None:
        """Initialize the base model.

        Args:
            data: The dataset to build the model from.
        """
        self.model = Model("OptimizationModel")
        self.data: MultiEntityDataset = data
        self.vars: dict[type[Variable], Any] = {}
        self.added_vars: list[type[Variable]] = []
        self.added_constraints: list[type[Constraint]] = []

    def add_constr(self, *args, **kwargs) -> Constr:
        """Shortcut for ``self.model.addConstr``.

        Returns:
            The Gurobi constraint object.
        """
        return self.model.addConstr(*args, **kwargs)

    def build(
        self,
        variables: list[type[Variable]],
        constraints: list[type[Constraint]],
        **kwargs: Any,
    ) -> None:
        """Assemble the Gurobi model in phases.

        Args:
            variables: ``Variable`` subclasses to build (in order).
            constraints: ``Constraint`` subclasses to apply (in order).
            **kwargs: Parameters forwarded to constraints
                (e.g. ``n_hubs``, ``alpha``).

        Raises:
            ValueError: If a variable is added twice or if
                ``required_vars`` are missing for a constraint.
        """
        for var_cls in variables:
            if var_cls in self.added_vars:
                raise ValueError(
                    f"{var_cls.__name__} has already been added to the model."
                )
            var_value = var_cls.var_metadata.value
            for existing in self.added_vars:
                if existing.var_metadata.value == var_value:
                    raise ValueError(
                        f"Variable value '{var_value}' conflict: "
                        f"'{var_cls.__name__}' and '{existing.__name__}' "
                        f"cannot both be in the same model."
                    )
            self.vars[var_cls] = var_cls().build(self)
            self.added_vars.append(var_cls)

        for con_cls in constraints:
            con = con_cls()
            missing_vars = [v for v in con.required_vars if v not in self.vars]
            if missing_vars:
                raise ValueError(
                    f"{con_cls.__name__} requires variables "
                    f"{missing_vars} that were not built. "
                    f"Add them to the 'variables' list."
                )
            con.build(self, **kwargs)
            self.added_constraints.append(con_cls)

        result = self._set_objective(**kwargs)
        if result is not None:
            self.model.setObjective(*result)

        self.model.update()

    def _set_objective(self, **kwargs):
        """Override in subclasses to define the optimization objective.

        Args:
            **kwargs: Parameters forwarded from ``build()``.

        Returns:
            ``(expression, sense)`` tuple for ``model.setObjective``,
            or ``None`` if the objective is set elsewhere.
        """
        return None

    def get_model(self) -> Model:
        """Return the underlying Gurobi model."""
        return self.model

    @property
    def model_name(self) -> ModelMetaData:
        """Return the model's metadata.

        Falls back to the ``model_metadata`` class attribute if set,
        otherwise returns a default using the class name.
        """
        if hasattr(self, 'model_metadata'):
            return self.model_metadata
        return ModelMetaData(
            value=type(self).__name__,
            display_name=type(self).__name__,
        )
        