from typing import List, Dict

from bilevelpy.benchmarks.abstract_refreshing_service import AbstractRefreshingService
from bilevelpy.benchmarks.config import BenchmarkConfig
from bilevelpy.benchmarks.protocols import ModelProvider


class BenchmarkRunner(AbstractRefreshingService):
    def __init__(self, config: BenchmarkConfig, provider: ModelProvider):
        super().__init__()
        self.config = config
        self.provider = provider
        self.results: List[Dict] = []


    def run(self):
        total_steps = len(self.config.scenarios) * len(self.config.methods) * self.config.n_runs

        self.on_all_refreshables(lambda r: r.refresh_after_benchmark_start(total_steps, self.config))

        for scenario in self.config.scenarios:
            self.on_all_refreshables(lambda r: r.refresh_after_scenario_start(scenario))
            scenario_solutions = []
            for run_idx in range(self.config.n_runs):
                run_solutions = []
                run_summaries = []
                self.on_all_refreshables(lambda r: r.refresh_after_run_start(scenario, run_idx))
                for method in self.config.methods:
                    seed = self.config.seeds[run_idx]
                    skip = False

                    def _mark_if_sanctioned(refreshable):
                        nonlocal skip
                        try:
                            if refreshable.is_method_sanctioned(scenario, method):
                                skip = True
                        except Exception:
                            # if refreshable does not implement the query, ignore
                            pass

                    self.on_all_refreshables(_mark_if_sanctioned)

                    if skip:
                        # Inform refreshables about the skip (optional hook) and record a skipped entry
                        self.on_all_refreshables(lambda r: r.refresh_after_method_skipped(scenario, method, run_idx, seed))
                        res_entry = {**scenario, "method": method, "run": run_idx, "skipped": True, "sanctioned": True}
                        self.results.append(res_entry)
                        run_summaries.append(res_entry)
                        # Don't run this method
                        continue

                    # Normal execution: inform refreshables that method is starting
                    self.on_all_refreshables(lambda r: r.refresh_after_method_start(scenario, method, run_idx, seed))

                    try:
                        solution = self.provider.build_and_solve(model_name=method,
                                                                  scenario=scenario,
                                                                  run_idx=run_idx,
                                                                  seed=seed)
                    except Exception as e:
                        self.on_all_refreshables(
                            lambda r: r.refresh_after_solution_error(scenario, method, run_idx, seed, e))

                        res_entry = {**scenario, "method": method, "run": run_idx, "error": str(e)}
                        self.results.append(res_entry)
                        run_summaries.append(res_entry)
                        continue

                    metadata_dict = solution.solution_metadata.to_dict(with_label=False)
                    res_entry = {**scenario, "method": method, "run": run_idx, **metadata_dict}
                    self.results.append(res_entry)

                    run_solution = {
                        **scenario,
                        "method": method,
                        "run": run_idx,
                        "_solution_metadata": solution.solution_metadata,
                        "_solution_data": solution.solution_data,
                    }
                    run_solutions.append(run_solution)
                    run_summaries.append(res_entry)


                    self.on_all_refreshables(lambda r: r.refresh_after_method_end(scenario, method, run_idx, seed, solution))

                    solution.dispose()

                scenario_solutions.append(run_summaries)

                self.on_all_refreshables(lambda r: r.refresh_after_run_end(scenario, run_idx, run_solutions))


                try:
                    run_solutions.clear()
                except Exception:
                    pass
                try:
                    import gc

                    gc.collect()
                except Exception:
                    pass

            self.on_all_refreshables(lambda r: r.refresh_after_scenario_end(scenario, scenario_solutions))

        self.on_all_refreshables(lambda r: r.refresh_after_benchmark_end(self.results))
