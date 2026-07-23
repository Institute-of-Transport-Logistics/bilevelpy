from dataclasses import dataclass, field
from typing import List, Dict, Any

from bilevelpy.models.meta import ModelMetaData


@dataclass
class BenchmarkConfig:
    """Configuration for a benchmark experiment.

    Attributes:
        name: Human-readable name for this benchmark.
        methods: List of [ModelMetaData][bilevelpy.models.meta.ModelMetaData]
            entries, one per model method to compare.
        scenarios: List of parameter dictionaries. Each scenario is one
            row in the benchmark grid.
        n_runs: Number of repetitions per scenario.
        seeds: List of random seeds (one per run). Defaults to 1–10.
    """

    name: str
    methods: List[ModelMetaData]
    scenarios: List[Dict[str, Any]]
    n_runs: int = 1
    seeds: List[int] = field(default_factory=lambda: list(range(1, 11)))
