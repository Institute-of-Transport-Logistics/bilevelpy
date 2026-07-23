from __future__ import annotations

import os
from typing import Any, TYPE_CHECKING

from gurobipy import Model

from bilevelpy.models.core import BaseModel
from bilevelpy.solution.solution_registry import SolutionRegistry

if TYPE_CHECKING:
    from bilevelpy.solution.core import BaseModelSolution


class ModelSolver:
    """Solver for hub location-allocation models using Gurobi.

    Wraps a [BaseModel][bilevelpy.models.core.BaseModel] with Gurobi parameter
    configuration and provides ``solve()`` to return a parsed solution.

    Attributes:
        _model (BaseModel): The hub location-allocation model instance to be solved.
        _gurobi_model (gurobipy.Model): The underlying Gurobi optimization model object
            extracted from the _model instance.
        _time_limit (int | None): Time limit in seconds for the Gurobi solver.
            If None, no time limit is imposed. Defaults to None.
        _mip_gap (float | None): Relative MIP gap tolerance for solver termination.
            Values between 0 and 1 represent percentage gaps. If None, uses Gurobi's default.
        _use_max_threads (bool): If True, Gurobi uses all available CPU threads.
            If False, restricts to single-threaded execution for reproducibility.
        _params (dict): Dictionary containing gurobi model parameters to be used
    """

    _model: BaseModel
    _gurobi_model: Model
    _time_limit: int | None
    _mip_gap: float | None
    _use_max_threads: bool
    _params: dict

    def __init__(
        self,
        model: BaseModel,
        time_limit: int = None,
        mip_gap: float = None,
        use_max_threads: bool = False,
        int_feas_tol: float = 1e-9,
        extra_params: dict[str, Any] | None = None,
    ):
        """Configure Gurobi parameters and prepare the model for solving.

        Args:
            model: A [BaseModel][bilevelpy.models.core.BaseModel] instance to solve.
            time_limit: Maximum time in seconds for the solver to run.
                If None, no time limit is applied. Defaults to None.
            mip_gap: Relative MIP gap tolerance for solver termination.
                Should be a value between 0 and 1 (e.g., 0.01 for 1% gap).
                If None, Gurobi's default tolerance is used. Defaults to None.
            use_max_threads: If True, uses all available CPU cores for parallel solving.
                If False, restricts to single-threaded execution for reproducible results.
                Defaults to False.
            extra_params: Dictionary of additional Gurobi parameters to pass through.

        Raises:
            TypeError: If *model* is not a [BaseModel][bilevelpy.models.core.BaseModel] instance.
        """


        if not isinstance(model, BaseModel):
            raise TypeError(f"Expected BaseModel, got {type(model).__name__}")
        self._model = model
        self._gurobi_model = self._model.get_model()

        self._params = {
            "TimeLimit": time_limit,
            "MIPGap": mip_gap,
            "Threads": 0 if use_max_threads else 1,
            "IntFeasTol": int_feas_tol
        }


        if extra_params:
            clean_extras = {k: v for k, v in extra_params.items() if v is not None}
            self._params.update(clean_extras)

        self.__setup_solver()

    def __setup_solver(self) -> None:
        """Apply stored Gurobi parameters to the underlying model."""
        for param, value in self.params.items():
            if value is not None:
                self._gurobi_model.setParam(param, value)

    def solve(self) -> BaseModelSolution:
        """Optimize the model and return a parsed solution.

        Raises:
            RuntimeError: If the model is infeasible (writes IIS to disk).
            NotImplementedError: If no solution class is registered for this model
                via [SolutionRegistry][bilevelpy.solution.solution_registry.SolutionRegistry].

        Examples:
            ```python
            solver = ModelSolver(model, time_limit=3600)
            solution = solver.solve()
            print(f"Objective: {solution.solution_metadata.objective_value}")
            ```
        """
        from gurobipy import GRB

        self._gurobi_model.optimize()

        status = self._gurobi_model.Status
        if status == GRB.INFEASIBLE:
            filename = "model_infeasible.ilp"

            abs_path = os.path.abspath(filename)

            print(f"\n[WARNING] Model is Infeasible. Computing IIS (Irreducible Inconsistent Subsystem)...")
            self._gurobi_model.computeIIS()
            self._gurobi_model.write(filename)

            raise RuntimeError(
                f"Optimization failed: Model is Infeasible.\n"
                f"The conflict report has been saved to:\n{abs_path}"
            )

        # Dynamically grab the correct solution class based on the model type
        solution_class = SolutionRegistry.get_solution_class(type(self._model))

        if not solution_class:
            raise NotImplementedError(
                f"No solution parser is registered in the SolutionRegistry for {type(self._model).__name__}. "
                "Did you forget to add the @SolutionRegistry.register_for decorator?"
            )

        # Instantiate and return the parsed solution!
        return solution_class(self)

    @property
    def params(self):
        return self._params

    @property
    def model(self) -> BaseModel:
        """Get the underlying [BaseModel][bilevelpy.models.core.BaseModel] instance.

        Returns:
            BaseModel: The model that was provided during initialization.
        """
        return self._model
