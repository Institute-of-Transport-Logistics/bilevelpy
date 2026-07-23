from typing import Protocol, Dict, Any, List

from bilevelpy.benchmarks.config import BenchmarkConfig
from bilevelpy.models.meta import ModelMetaData
from bilevelpy.solution import BaseModelSolution

class ModelProvider(Protocol):
    """Protocol for bridging benchmarks to specific model implementations.

    Implementations build a model from a scenario, solve it, and return
    a [BaseModelSolution][bilevelpy.solution.BaseModelSolution].
    """

    def build_and_solve(
        self,
        model_name: ModelMetaData,
        scenario: Dict[str, Any],
        run_idx: int,
        seed: int,
    ) -> BaseModelSolution:
        """Build and solve a model for a given scenario and run.

        Args:
            model_name: Which model to build.
            scenario: Parameter dictionary (e.g. ``{"n_hubs": 2, ...}``).
            run_idx: Which repetition this is (0-indexed).
            seed: Random seed for reproducibility.

        Returns:
            The solution produced by the solver.
        """
        ...


class BenchmarkRefreshable:
    """Interface for benchmark lifecycle hooks.

    Subclass and override any of these methods to add behavior at
    specific points during benchmark execution (logging, progress
    reporting, archiving, etc.). All methods are no-ops by default.
    """

    def refresh_after_benchmark_start(self, total_steps: int, config: BenchmarkConfig) -> None:
        """Called once when the benchmark starts."""

    def refresh_after_benchmark_end(self, all_results: list) -> None:
        """Called once when the benchmark finishes."""

    def refresh_after_scenario_start(self, scenario: Dict[str, Any]) -> None:
        """Called when a new scenario begins."""

    def refresh_after_scenario_end(self, scenario: Dict[str, Any], solutions: List[BaseModelSolution]) -> None:
        """Called when a scenario completes."""

    def refresh_after_run_start(self, scenario: Dict[str, Any], run_idx: int) -> None:
        """Called at the start of each repetition."""

    def refresh_after_run_end(self, scenario: Dict[str, Any], run_idx: int, results: List[BaseModelSolution]) -> None:
        """Called at the end of each repetition."""

    def refresh_after_method_start(self, scenario: Dict[str, Any], method: ModelMetaData, run_idx: int, seed: int) -> None:
        """Called before building/solving a specific method."""

    def refresh_after_solution_error(self, scenario: Dict[str, Any], method: ModelMetaData, run_idx: int, seed: int, error: Exception) -> None:
        """Called when ``build_and_solve`` raises an exception."""

    def refresh_after_method_end(self, scenario: Dict[str, Any], method: ModelMetaData, run_idx: int, seed: int, solution: BaseModelSolution) -> None:
        """Called after a method completes successfully."""

    def refresh_after_method_skipped(self, scenario: Dict[str, Any], method: ModelMetaData, run_idx: int, seed: int) -> None:
        """Called when the runner skips a method (e.g. sanctioning)."""

    def is_method_sanctioned(self, scenario: Dict[str, Any], method: ModelMetaData) -> bool:
        """Return ``True`` to skip a method. Default: ``False``."""
        return False


