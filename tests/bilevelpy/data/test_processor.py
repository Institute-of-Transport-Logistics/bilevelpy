"""Tests for HLPNodeSelector and HLPCostScaling."""

import pytest

from bilevelpy.core.columns import DataCol
from bilevelpy.core.datasets import Dataset
from bilevelpy.data.core import MultiEntityDataset
from bilevelpy.data.loaders import HLPLoader
from bilevelpy.data.processor import HLPNodeSelector, HLPCostScaling



# Tests of the HLPNodeSelector
class TestHLPNodeSelector:

    class TestInit:
        def test_defaults(self):
            sel = HLPNodeSelector(n_nodes=5)
            assert sel.n_nodes == 5
            assert sel.random_nodes is False
            assert sel.random_obj is not None

        def test_random_mode(self):
            sel = HLPNodeSelector(n_nodes=5,
                                                    random_nodes=True,
                                                    seed=123)
            assert sel.random_nodes is True

    class TestProcess:
        @pytest.fixture(scope="class")
        def cab25(self) -> MultiEntityDataset:
            ds = MultiEntityDataset()
            HLPLoader(Dataset.CAB25).process(ds)
            return ds

        def test_selects_exactly_n_nodes(self, cab25):
            HLPNodeSelector(n_nodes=10).process(cab25)
            assert len(cab25[DataCol.NODE_ID]) == 10

        def test_filters_cost_entity(self, cab25):
            HLPNodeSelector(n_nodes=8).process(cab25)
            assert len(cab25[DataCol.COST_NODE_TO_NODE]) == 8 * 8

        def test_filters_weight_entity(self, cab25):
            HLPNodeSelector(n_nodes=6).process(cab25)
            assert len(cab25[DataCol.WEIGHTS_NODE_TO_NODE]) == 6 * 6

        def test_node_ids_are_head_of_sorted_list(self, cab25):
            HLPNodeSelector(n_nodes=5).process(cab25)
            ids = sorted(k[0] for k in cab25[DataCol.NODE_ID])
            assert ids == [0, 1, 2, 3, 4]

        def test_n_nodes_exceeds_available_raises(self, cab25):
            with pytest.raises(ValueError):
                HLPNodeSelector(n_nodes=999).process(cab25)

        def test_missing_node_id_raises(self):
            with pytest.raises(AttributeError):
                HLPNodeSelector(n_nodes=5).process(MultiEntityDataset())

        def test_missing_cost_raises(self):
            ds = MultiEntityDataset()
            ds.add_entity(DataCol.NODE_ID, [DataCol.NODE_ID], {(0,): 0})
            with pytest.raises(AttributeError):
                HLPNodeSelector(n_nodes=1).process(ds)

    class TestRandomMode:
        def test_selects_n_nodes(self):
            ds = MultiEntityDataset()
            HLPLoader(Dataset.CAB25).process(ds)
            HLPNodeSelector(n_nodes=7, random_nodes=True, seed=42).process(ds)
            assert len(ds[DataCol.NODE_ID]) == 7

        def test_reproducible_with_same_seed(self):
            def selected_ids(seed):
                ds = MultiEntityDataset()
                HLPLoader(Dataset.CAB25).process(ds)
                HLPNodeSelector(n_nodes=5, random_nodes=True, seed=seed).process(ds)
                return sorted(k[0] for k in ds[DataCol.NODE_ID])

            assert selected_ids(42) == selected_ids(42)
            assert selected_ids(7) == selected_ids(7)



# Tests of the HLPCostScaling
class TestHLPCostScaling:

    class TestInit:
        def test_stores_factor(self):
            scaler = HLPCostScaling(scaling_factor=100.0)
            assert scaler.scaling_factor == 100.0

    class TestProcess:
        @pytest.fixture(scope="class")
        def cab25(self) -> MultiEntityDataset:
            ds = MultiEntityDataset()
            HLPLoader(Dataset.CAB25).process(ds)
            return ds

        def test_scales_all_costs_by_factor(self, cab25):
            cost_before = dict(cab25[DataCol.COST_NODE_TO_NODE].items())
            HLPCostScaling(scaling_factor=10.0).process(cab25)
            for keys, val_before in cost_before.items():
                expected = val_before / 10.0
                assert cab25[DataCol.COST_NODE_TO_NODE][keys] == pytest.approx(expected)

        def test_zero_costs_remain_zero(self, cab25):
            HLPCostScaling(scaling_factor=50.0).process(cab25)
            cost = cab25[DataCol.COST_NODE_TO_NODE]
            for i in range(25):
                assert cost[i, i] == pytest.approx(0.0, abs=1e-6)

        def test_weights_are_untouched(self, cab25):
            weight_before = dict(cab25[DataCol.WEIGHTS_NODE_TO_NODE].items())
            HLPCostScaling(scaling_factor=100.0).process(cab25)
            for keys, val_before in weight_before.items():
                assert cab25[DataCol.WEIGHTS_NODE_TO_NODE][keys] == val_before

        def test_missing_cost_raises(self):
            with pytest.raises(AttributeError):
                HLPCostScaling(scaling_factor=2.0).process(MultiEntityDataset())