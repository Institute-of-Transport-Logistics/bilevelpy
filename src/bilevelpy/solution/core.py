import gc
from abc import ABC
from dataclasses import dataclass, field, asdict
from enum import StrEnum
from typing import Dict, Any
from gurobipy import GRB, Model


from bilevelpy.data.core import MultiEntityDataset
from bilevelpy.models.core import BaseModel
from bilevelpy.solver.solver import ModelSolver
from bilevelpy.solution.utils import extract_gurobi_name
from bilevelpy.models.meta import ModelMetaData, VariableMetaData
from bilevelpy.models.vars.core import Variable



class SolutionLabels(StrEnum):
    solving_time = "Solving Time (s)"
    objective_value = "Objective Value"
    is_optimal = "Is Optimal"
    mip_gap = "MIP Gap (%)"
    node_count = "Nodes Explored"


@dataclass
class SolutionMetadata:
    """A pure data container for solver metrics."""
    solving_time: float
    objective_value: float | None
    is_optimal: bool
    mip_gap: float
    node_count: int
    extra: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_model(cls, model: Model) -> "SolutionMetadata":
        """Factory method: extracts the data from the Gurobi model and builds the class."""
        return cls(
        solving_time=model.Runtime,
        objective_value=model.ObjVal if model.Status in [GRB.OPTIMAL, GRB.TIME_LIMIT] else None,
        is_optimal=(model.Status == GRB.OPTIMAL),
        mip_gap=model.MIPGap if hasattr(model, "MIPGap") else 0.0,
        node_count=int(model.NodeCount)
    )

    def _translate(self, key: str) -> str:
        """Translates internal attribute names to human-readable labels."""
        try:
            return SolutionLabels[key].value
        except KeyError:
            return key  # Fallback to the original key if no translation exists

    def to_dict(self, with_label: bool = False) -> dict:
        raw_data = asdict(self)
        extra = raw_data.pop("extra", {})

        for key in extra:
            if key in raw_data:
                raise ValueError(f"Key collision: '{key}' already exists in SolutionMetadata")

        raw_data.update(extra)

        formatted_data = {}
        for k, v in raw_data.items():
            new_key = self._translate(k) if with_label else k
            formatted_data[new_key] = v


        return formatted_data



class BaseModelSolution(ABC):
    _solver: ModelSolver
    _gurobi_model: Model
    _model: BaseModel
    _solution_metadata: SolutionMetadata
    _dict_solution: dict[VariableMetaData, dict[tuple, float]]
    _solution_data: MultiEntityDataset

    def __init__(self, model_solver: ModelSolver):
        self._solver = model_solver
        self._gurobi_model = model_solver.model.get_model()
        self._model = model_solver.model

        self._solution_metadata = SolutionMetadata.from_model(self._gurobi_model)

        self._name_to_var_obj: Dict[str, VariableMetaData] = {}
        for var_cls in self._model.vars:
            if isinstance(var_cls, type) and issubclass(var_cls, Variable):
                meta = var_cls.var_metadata
                self._name_to_var_obj[meta.value] = meta

        self._dict_solution, self._solution_data = self.__extract_solution()

        self.variables = list(self._dict_solution.keys())

        self._register_custom_entities()

    def __extract_solution(self) -> tuple[dict[VariableMetaData, dict[tuple, float]], MultiEntityDataset]:
        """Greedy extraction of all primal variables."""

        dict_solution = {}
        dataset = MultiEntityDataset()

        for v in self._gurobi_model.getVars():
            base_str, idx = extract_gurobi_name(v.VarName)

            var_obj = self._name_to_var_obj.get(base_str)
            if not var_obj:
                continue

            if not self._should_keep_variable(var_obj, idx):
                continue

            if var_obj not in dict_solution:
                dict_solution[var_obj] = {}

            dict_solution[var_obj][idx] = v.X

        for var_obj, data_map in dict_solution.items():
            dataset.add_entity(
                name=var_obj,
                keys=var_obj.identifiers,
                data_map=data_map
            )

        return dict_solution, dataset

    def _should_keep_variable(self, base_name: VariableMetaData, indices: tuple) -> bool:
        """Hook for basic filtering. Mixins can override or extend this."""
        return True

    def _get_model_specific_summary(self) -> list[str]:
        """Hook method for subclasses to add specific summary lines.


        Returns:

        list[str]: A list of formatted strings to insert into the summary.

        """
        return []

    def _register_custom_entities(self):
        """Hook for subclasses/Mixins to add derived logic to the dataset."""
        pass

    @property
    def model_name(self) -> ModelMetaData:
        return self._model.model_name

    @property
    def display_name(self) -> str:
        return self.model_name.display_name

    @property
    def solution_data(self) -> MultiEntityDataset:
        return self._solution_data

    @property
    def solution_metadata(self) -> SolutionMetadata:
        return self._solution_metadata


    def __str__(self) -> str:
        lines = []
        lines.append("=" * 50)
        lines.append(f"SOLUTION SUMMARY: {self.display_name}")
        lines.append("=" * 50)

        # Clean variable display
        var_list = ", ".join([v.display_name for v in self.variables])
        lines.append(f"Variables Extracted : {var_list}")

        lines.append("-" * 50)
        lines.append("Gurobi Configuration:")
        for key, value in self._solver.params.items():
            if value is not None:
                lines.append(f"  {key:12}: {value}")

        lines.append("-" * 50)
        lines.append("Solution Metadata:")
        meta = self._solution_metadata.to_dict(with_label=True)
        for key, value in meta.items():
            lines.append(f"  {key:18}: {value}")

        lines.extend(self._get_model_specific_summary())
        lines.append("=" * 50)
        return "\n".join(lines)

    def __getitem__(self, item):
        """Support dict-like indexing to retrieve dataframes or specific values.
        """
        if isinstance(item, VariableMetaData):
            return self._solution_data[item]

    def dispose(self) -> None:
        """Release heavy references (Gurobi model / solver) to free memory.

        This attempts to call the gurobipy Model.dispose() if available and
        removes references to the solver and Gurobi model so the Python
        garbage collector can reclaim memory. Call this after all required
        data has been extracted from the solution.
        """
        self._gurobi_model.dispose()  # Attempt to dispose the Gurobi model (best-effort)
        self._gurobi_model = None
        self._solver = None

        gc.collect()



