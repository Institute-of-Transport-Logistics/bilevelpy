from typing import Callable, List

from bilevelpy.benchmarks.protocols import BenchmarkRefreshable


class AbstractRefreshingService:
    """Holds [BenchmarkRefreshable][bilevelpy.benchmarks.protocols.BenchmarkRefreshable] objects
    and applies actions to all of them."""

    def __init__(self):
        self._refreshables: List[BenchmarkRefreshable] = []

    def add_refreshable(self, new_refreshable: BenchmarkRefreshable) -> None:
        self._refreshables.append(new_refreshable)

    def on_all_refreshables(self, action: Callable[[BenchmarkRefreshable], None]) -> None:
        """
        Takes a lambda function and applies it to every registered refreshable.
        This completely hides the 'for' loops from your child classes.
        """
        for refreshable in self._refreshables:
            action(refreshable)