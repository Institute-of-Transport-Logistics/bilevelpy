"""Tests for HLPLoader — CAB25 and CAB100 dataset loading."""

import pytest

from bilevelpy.core.columns import DataCol
from bilevelpy.core.datasets import Dataset
from bilevelpy.data.core import MultiEntityDataset
from bilevelpy.data.loaders import HLPLoader



class TestBundledDatasetFiles:
    """Sanity-check that the raw dataset files ship with the package."""

    def test_cab25_file_exists(self):
        loader = HLPLoader(Dataset.CAB25)
        assert loader._resource.is_file(), (
            f"CAB25 dataset not found at {loader._resource}"
        )

    def test_cab100_file_exists(self):
        loader = HLPLoader(Dataset.CAB100)
        assert loader._resource.is_file(), (
            f"CAB100 dataset not found at {loader._resource}"
        )




class TestHLPLoaderInit:
    def test_default_dataset_is_cab25(self):
        loader = HLPLoader()
        assert loader._dataset == Dataset.CAB25

    @pytest.mark.parametrize("dataset_enum,filename", [
        (Dataset.CAB25,  "cab25.txt"),
        (Dataset.CAB100, "cab100.txt"),
    ])
    def test_resource_points_to_expected_filename(self, dataset_enum, filename):
        loader = HLPLoader(dataset_enum)
        assert loader._dataset == dataset_enum
        assert loader._resource.name == filename



class TestLoadCABDatasetsProperties:
    """Properties that hold for both CAB25 and CAB100."""

    @pytest.fixture(
        scope="class",
        params=[(Dataset.CAB25, 25),
                        (Dataset.CAB100, 100)],
        ids=["CAB25",
             "CAB100"],
    )
    def loaded(self, request) -> tuple[int, MultiEntityDataset]:
        dataset_enum, n = request.param
        loader = HLPLoader(dataset_enum)
        ds = MultiEntityDataset()
        loader.process(ds)
        return n, ds

    def test_creates_three_entities(self, loaded):
        _, ds = loaded
        assert len(ds) == 3
        assert DataCol.COST_NODE_TO_NODE in ds
        assert DataCol.WEIGHTS_NODE_TO_NODE in ds
        assert DataCol.NODE_ID in ds

    class TestCost:
        def test_name_and_keys(self, loaded):
            _, ds = loaded
            cost = ds[DataCol.COST_NODE_TO_NODE]
            assert cost.name == DataCol.COST_NODE_TO_NODE
            assert cost.keys == [DataCol.START_NODE, DataCol.END_NODE]

        def test_has_n_squared_entries(self, loaded):
            n, ds = loaded
            assert len(ds[DataCol.COST_NODE_TO_NODE]) == n * n

        def test_zero_indexed(self, loaded):
            n, ds = loaded
            cost = ds[DataCol.COST_NODE_TO_NODE]
            assert (0, 0) in cost
            assert (n - 1, n - 1) in cost
            assert (n, n) not in cost

        def test_self_loops_are_zero(self, loaded):
            n, ds = loaded
            cost = ds[DataCol.COST_NODE_TO_NODE]
            for i in range(n):
                assert cost[i, i] == pytest.approx(0.0, abs=1e-6)

    class TestWeight:
        def test_name_and_keys(self, loaded):
            _, ds = loaded
            weight = ds[DataCol.WEIGHTS_NODE_TO_NODE]
            assert weight.name == DataCol.WEIGHTS_NODE_TO_NODE
            assert weight.keys == [DataCol.START_NODE, DataCol.END_NODE]

        def test_has_n_squared_entries(self, loaded):
            n, ds = loaded
            assert len(ds[DataCol.WEIGHTS_NODE_TO_NODE]) == n * n

        def test_self_loops_are_zero(self, loaded):
            n, ds = loaded
            weight = ds[DataCol.WEIGHTS_NODE_TO_NODE]
            for i in range(n):
                assert weight[i, i] == pytest.approx(0.0, abs=1e-6)

    class TestNodes:
        def test_name_and_keys(self, loaded):
            _, ds = loaded
            nodes = ds[DataCol.NODE_ID]
            assert nodes.name == DataCol.NODE_ID
            assert nodes.keys == [DataCol.NODE_ID]

        def test_has_n_entries(self, loaded):
            n, ds = loaded
            assert len(ds[DataCol.NODE_ID]) == n

        def test_ids_are_zero_to_n_minus_one(self, loaded):
            n, ds = loaded
            node_ids = sorted(k[0] for k in ds[DataCol.NODE_ID])
            assert node_ids == list(range(n))





class TestHLPLoaderProcessCAB25Values:
    """Spot-check known values from the CAB25 file."""

    @pytest.fixture(scope="class")
    def dataset(self) -> MultiEntityDataset:
        loader = HLPLoader(Dataset.CAB25)
        ds = MultiEntityDataset()
        loader.process(ds)
        return ds

    def test_cost_known_value(self, dataset):
        """CAB25 line 2: '1 2 6469. 576.9631' → cost at (0,1)."""
        cost = dataset[DataCol.COST_NODE_TO_NODE]
        assert cost[0, 1] == pytest.approx(576.9631, abs=1e-6)

    def test_weight_known_value(self, dataset):
        """CAB25 line 2: '1 2 6469. 576.9631' → weight at (0,1)."""
        weight = dataset[DataCol.WEIGHTS_NODE_TO_NODE]
        assert weight[0, 1] == pytest.approx(6469.0, abs=1e-6)



class TestHLPLoaderIntegration:
    @pytest.mark.parametrize("dataset_enum",
                                                [Dataset.CAB25,
                                                Dataset.CAB100])
    def test_builder_pipeline(self, dataset_enum):
        from bilevelpy.data.builder import DatasetBuilder

        dataset = DatasetBuilder().pipe(HLPLoader(dataset_enum)).build()
        assert len(dataset) == 3
        assert DataCol.COST_NODE_TO_NODE in dataset