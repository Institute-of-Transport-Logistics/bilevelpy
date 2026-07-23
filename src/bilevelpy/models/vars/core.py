from abc import abstractmethod, ABC, ABCMeta
from typing import TYPE_CHECKING

from gurobipy import tupledict

from bilevelpy.models.meta import VariableMetaData

if TYPE_CHECKING:
    from bilevelpy.models.core import BaseModel


class VariableMeta(ABCMeta):
    """Makes Variable subclasses usable as dict keys, delegating to var_metadata."""

    def __hash__(cls) -> int:
        return hash(cls.var_metadata)

    def __eq__(cls, other) -> bool:
        if isinstance(other, VariableMeta):
            return cls.var_metadata == other.var_metadata
        if isinstance(other, VariableMetaData):
            return cls.var_metadata == other
        if isinstance(other, str):
            return cls.var_metadata == other
        return False

    def __str__(cls) -> str:
        return cls.var_metadata.value

    def __repr__(cls) -> str:
        return f"<Variable: '{cls.var_metadata.value}'>"


class Variable(ABC, metaclass=VariableMeta):
    var_metadata: VariableMetaData

    @abstractmethod
    def build(self, model: "BaseModel") -> tupledict:
        """Create Gurobi variables and return them.

        BaseModel stores the returned tupledict in ``self.vars`` keyed
        by the subclass, so constraints can access them via
        ``model.vars[AllocationVariable]``.
        """
        ...

    def validate(self, model: "BaseModel") -> None:
        pass
