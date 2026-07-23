"""Tests for DatasetBuilder — pipeline assembly and execution."""

import pytest

from bilevelpy.core.columns import DataCol
from bilevelpy.core.datasets import Dataset
from bilevelpy.data.base_processor import EntityProcessor
from bilevelpy.data.builder import DatasetBuilder
from bilevelpy.data.core import MultiEntityDataset
from bilevelpy.data.loaders import HLPLoader



# Test processor for verifying call ordering
class TestProcessor(EntityProcessor):
    """Records every ``process()`` call into a shared list for assertions."""

    def __init__(self, name: str, log: list[str]):
        self.name = name
        self._log = log

    def process(self, dataset: MultiEntityDataset) -> None:
        self._log.append(self.name)



# Tests of Initiator
class TestDatasetBuilderInit:

    class TestDataset:
        def test_is_empty_multi_entity_dataset(self):
            builder = DatasetBuilder()
            ds = builder._dataset
            assert isinstance(ds, MultiEntityDataset)
            assert len(ds) == 0

    class TestProcessors:
        def test_is_empty_list(self):
            builder = DatasetBuilder()
            assert builder._processors == []



# Tests of the pipe() method
class TestDatasetBuilderPipe:

    def test_appends_processor(self):
        builder = DatasetBuilder()
        log: list[str] = []
        builder.pipe(TestProcessor("a", log))
        assert len(builder._processors) == 1

    def test_returns_self(self):
        builder = DatasetBuilder()
        log: list[str] = []
        result = builder.pipe(TestProcessor("a", log))
        assert result is builder

    class TestOrdering:
        def test_processors_stored_in_insertion_order(self):
            builder = DatasetBuilder()
            log: list[str] = []
            builder.pipe(TestProcessor("a", log))
            builder.pipe(TestProcessor("b", log))
            builder.pipe(TestProcessor("c", log))
            names = [p.name for p in builder._processors]
            assert names == ["a", "b", "c"]

    class TestFluentChaining:
        def test_multiple_pipes_in_one_expression(self):
            log: list[str] = []
            builder = (
                DatasetBuilder()
                .pipe(TestProcessor("a", log))
                .pipe(TestProcessor("b", log))
                .pipe(TestProcessor("c", log))
            )
            assert len(builder._processors) == 3



# Tests of build() method
class TestDatasetBuilderBuild:

    class TestEmptyPipeline:
        def test_returns_multi_entity_dataset(self):
            result = DatasetBuilder().build()
            assert isinstance(result, MultiEntityDataset)

        def test_returns_empty_dataset(self):
            result = DatasetBuilder().build()
            assert len(result) == 0

    class TestCallOrder:
        def test_processors_called_in_insertion_order(self):
            log: list[str] = []
            DatasetBuilder() \
                .pipe(TestProcessor("first", log)) \
                .pipe(TestProcessor("second", log)) \
                .pipe(TestProcessor("third", log)) \
                .build()
            assert log == ["first", "second", "third"]

        def test_each_processor_called_exactly_once(self):
            log: list[str] = []
            DatasetBuilder() \
                .pipe(TestProcessor("a", log)) \
                .pipe(TestProcessor("b", log)) \
                .build()
            assert log == ["a", "b"]

    class TestDatasetMutation:
        def test_same_dataset_passed_to_all_processors(self):
            """Each processor receives the same dataset instance."""

            seen_ids: list[int] = []

            class _IdRecorder(EntityProcessor):
                def process(self, dataset: MultiEntityDataset) -> None:
                    seen_ids.append(id(dataset))

            DatasetBuilder() \
                .pipe(_IdRecorder()) \
                .pipe(_IdRecorder()) \
                .build()
            assert len(seen_ids) == 2
            assert seen_ids[0] == seen_ids[1]

        def test_mutations_accumulate_across_processors(self):
            """A mutation by the first processor is visible to the second."""

            class _AddMarker(EntityProcessor):
                def process(self, dataset: MultiEntityDataset) -> None:
                    dataset.add_entity("marker", ["k"], {(0,): 1})

            class _VerifyMarker(EntityProcessor):
                def process(self, dataset: MultiEntityDataset) -> None:
                    assert "marker" in dataset
                    assert dataset["marker"][(0,)] == 1

            DatasetBuilder() \
                .pipe(_AddMarker()) \
                .pipe(_VerifyMarker()) \
                .build()



# Integration — real pipeline (load → filter → scale)
class TestDatasetBuilderIntegration:
    @pytest.fixture(scope="class")
    def dataset(self) -> MultiEntityDataset:
        from bilevelpy.data.processor import HLPNodeSelector, HLPCostScaling

        return (
            DatasetBuilder()
            .pipe(HLPLoader(Dataset.CAB25))
            .pipe(HLPNodeSelector(n_nodes=10))
            .pipe(HLPCostScaling(scaling_factor=100.0))
            .build()
        )

    def test_cost_entity_exists(self, dataset):
        assert DataCol.COST_NODE_TO_NODE in dataset

    def test_selected_only_10_nodes(self, dataset):
        assert len(dataset[DataCol.NODE_ID]) == 10

    def test_costs_have_100_entries(self, dataset):
        """10 × 10 = 100 cost entries after node selection."""
        assert len(dataset[DataCol.COST_NODE_TO_NODE]) == 10 * 10

    def test_costs_are_scaled(self, dataset):
        """Original CAB25 costs are on the order of hundreds; dividing
        by 100 should bring them into single digits."""
        cost = dataset[DataCol.COST_NODE_TO_NODE]
        for (_i, _j), val in cost.items():
            if val != pytest.approx(0.0, abs=1e-6):
                # non-zero costs should be < 20 after scaling by 100
                assert val < 20.0
