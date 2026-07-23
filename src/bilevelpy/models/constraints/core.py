from abc import ABC, abstractmethod
from typing import Any

from bilevelpy.models.vars.core import Variable


class Constraint(ABC):
    r"""Abstract base class for all optimization constraints.

    Subclasses declare which variables they require via ``required_vars``
    and implement :meth:`build` to add Gurobi constraints. The framework
    validates that all ``required_vars`` exist before calling ``build()``.

    Attributes:
        required_vars: List of [Variable][bilevelpy.models.vars.core.Variable] subclasses that must be
            built before this constraint can be applied.
    """

    required_vars: list[type[Variable]] = []

    @abstractmethod
    def build(self, model: "BaseModel", **kwargs: Any) -> None:
        """Add Gurobi constraints to the model.

        Args:
            model: The [BaseModel][bilevelpy.models.core.BaseModel] instance. Access variables via
                ``model.vars[VariableSubclass]``.
            **kwargs: Parameters forwarded from
                :meth:`BaseModel.build` (e.g. ``n_hubs``, ``alpha``).
        """
        ...