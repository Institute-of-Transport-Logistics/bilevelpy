"""Tests for EntityStore and MultiEntityDataset."""

import pytest

from bilevelpy.data.core import EntityStore, MultiEntityDataset


# EntityStore Tests
class TestEntityStore:

    # Construction Tests
    class TestConstruction:
        def test_stores_name_and_keys(self):
            store = EntityStore("cost", ["i", "j"], {(1, 2): 3.14})
            assert store.name == "cost"
            assert store.keys == ["i", "j"]

        def test_data_populated_at_init(self):
            store = EntityStore("w", ["from", "to"], {(0, 1): 10})
            assert len(store) == 1
            assert store[0, 1] == 10

        def test_set_data_replaces_all_entries(self):
            store = EntityStore("x", ["a"], {(0,): 1})
            store.set_data({(0,): 99, (1,): 100})
            assert len(store) == 2
            assert store[0] == 99

        def test_non_tuple_key_raises(self):
            with pytest.raises(TypeError):
                EntityStore("x", ["a", "b"], {(0, 1): 1, 2: 3})

        def test_key_length_mismatch_raises(self):
            with pytest.raises(ValueError):
                EntityStore("x", ["a", "b"], {(0, 1, 2): 5})

    # Access Tests
    class TestAccess:
        @pytest.fixture(scope="class")
        def store(self) -> EntityStore:
            return EntityStore("c", ["i", "j"], {
                (0, 0): 0.0, (0, 1): 5.0, (0, 2): 8.0,
                (1, 0): 5.0, (1, 1): 0.0,
            })

        def test_getitem_with_tuple(self, store):
            assert store[0, 1] == 5.0

        def test_getitem_with_scalar_wraps_to_tuple(self, store):
            store2 = EntityStore("n", ["id"], {(0,): 42})
            assert store2[0] == 42

        def test_getitem_missing_key_raises(self, store):
            with pytest.raises(KeyError):
                _ = store[99, 99]

        def test_call_no_args_returns_all(self, store):
            assert store() == store.data

        def test_call_with_prefix_filters(self, store):
            result = store(0)
            assert result == {(0, 0): 0.0, (0, 1): 5.0, (0, 2): 8.0}

        def test_find_by_value(self, store):
            keys = store.find_by_value(5.0)
            assert set(keys) == {(0, 1), (1, 0)}

        def test_items(self, store):
            assert list(store.items()) == list(store.data.items())

        def test_values(self, store):
            assert set(store.values) == {0.0, 5.0, 8.0}

        def test_data_property(self, store):
            assert store.data == store._data

    # Container  Tests
    class TestContainer:
        @pytest.fixture(scope="class")
        def store(self) -> EntityStore:
            return EntityStore("x", ["k"], {(0,): 10, (1,): 20})

        def test_len(self, store):
            assert len(store) == 2

        def test_iter_yields_keys(self, store):
            assert set(store) == {(0,), (1,)}

        def test_contains(self, store):
            assert (0,) in store
            assert (99,) not in store

        def test_contains_wraps_scalar(self, store):
            assert 0 in store

    # Conversion Tests
    class TestConversion:
        def test_to_dataframe_columns(self):
            store = EntityStore("c", ["from", "to"], {(0, 1): 3.14})
            df = store.to_dataframe()
            assert list(df.columns) == ["from", "to", "c"]

        def test_to_dataframe_values(self):
            store = EntityStore("w", ["i", "j"], {(0, 1): 10, (1, 2): 20})
            df = store.to_dataframe()
            assert len(df) == 2

        def test_to_dataframe_empty(self):
            store = EntityStore("e", ["k"], {})
            df = store.to_dataframe()
            assert list(df.columns) == ["k", "e"]
            assert len(df) == 0

    # Comparison Tests
    class TestComparison:
        def test_equal_stores(self):
            a = EntityStore("c", ["i", "j"], {(0, 1): 5.0, (0, 2): 8.0})
            b = EntityStore("c", ["i", "j"], {(0, 1): 5.0, (0, 2): 8.0})
            assert a == b

        def test_different_values_not_equal(self):
            a = EntityStore("c", ["i", "j"], {(0, 1): 5.0})
            b = EntityStore("c", ["i", "j"], {(0, 1): 99.0})
            assert a != b

        def test_different_key_sets_not_equal(self):
            a = EntityStore("c", ["i"], {(0,): 1})
            b = EntityStore("c", ["i"], {(1,): 1})
            assert a != b

        def test_different_key_length_not_equal(self):
            a = EntityStore("c", ["i"], {(0,): 1})
            b = EntityStore("c", ["i", "j"], {(0, 1): 1})
            assert a != b

        def test_non_entity_store_not_equal(self):
            assert EntityStore("x", ["k"], {(0,): 1}) != "not a store"

        def test_numerical_tolerance(self):
            a = EntityStore("c", ["i", "j"], {(0, 1): 1.000000001})
            b = EntityStore("c", ["i", "j"], {(0, 1): 1.000000002})
            assert a == b

    # Representation Tests
    class TestRepresentation:
        def test_str(self):
            s = str(EntityStore("c", ["i", "j"], {(0, 1): 3.14}))
            assert "EntityStore" in s
            assert "c" in s

        def test_repr(self):
            r = repr(EntityStore("c", ["i", "j"], {(0, 1): 3.14}))
            assert "EntityStore" in r


# MultiEntityDataset Tests
class TestMultiEntityDataset:

    # Construction Tests
    class TestConstruction:
        def test_starts_empty(self):
            ds = MultiEntityDataset()
            assert len(ds) == 0

        def test_add_entity_creates_store(self):
            ds = MultiEntityDataset()
            ds.add_entity("c", ["i", "j"], {(0, 1): 3.14})
            assert len(ds) == 1
            assert isinstance(ds["c"], EntityStore)

        def test_add_entity_overwrites_by_name(self):
            ds = MultiEntityDataset()
            ds.add_entity("c", ["i"], {(0,): 1})
            ds.add_entity("c", ["i"], {(1,): 2})
            assert len(ds) == 1
            assert ds["c"][1] == 2

    # Access Tests
    class TestAccess:
        @pytest.fixture(scope="class")
        def ds(self) -> MultiEntityDataset:
            d = MultiEntityDataset()
            d.add_entity("c", ["i", "j"], {(0, 1): 5.0})
            return d

        def test_getitem_returns_store(self, ds):
            assert ds["c"].name == "c"

        def test_getitem_missing_raises(self, ds):
            with pytest.raises(KeyError):
                _ = ds["nope"]

    # Container Tests
    class TestContainer:
        @pytest.fixture(scope="class")
        def ds(self) -> MultiEntityDataset:
            d = MultiEntityDataset()
            d.add_entity("c", ["i", "j"], {(0, 1): 1.0})
            d.add_entity("w", ["i", "j"], {(0, 1): 10.0})
            return d

        def test_len(self, ds):
            assert len(ds) == 2

        def test_iter_yields_names(self, ds):
            assert set(ds) == {"c", "w"}

        def test_contains(self, ds):
            assert "c" in ds
            assert "x" not in ds

    # Operations Tests
    class TestOperations:
        @pytest.fixture(scope="class")
        def ds_a(self) -> MultiEntityDataset:
            d = MultiEntityDataset()
            d.add_entity("c", ["i", "j"], {(0, 1): 5.0, (0, 2): 8.0})
            return d

        @pytest.fixture(scope="class")
        def ds_b(self) -> MultiEntityDataset:
            d = MultiEntityDataset()
            d.add_entity("w", ["i", "j"], {(0, 1): 10.0})
            return d

        def test_add_merges_datasets(self, ds_a, ds_b):
            combined = ds_a + ds_b
            assert len(combined) == 2
            assert "c" in combined
            assert "w" in combined

        def test_add_later_wins_on_conflict(self, ds_a):
            other = MultiEntityDataset()
            other.add_entity("c", ["i", "j"], {(99, 99): 999.0})
            combined = ds_a + other
            assert combined["c"][99, 99] == 999.0
            assert (0, 1) not in combined["c"]

        def test_add_original_unchanged(self, ds_a, ds_b):
            _ = ds_a + ds_b
            assert len(ds_a) == 1
            assert len(ds_b) == 1

        def test_join_merges_on_shared_keys(self, ds_a, ds_b):
            combined = ds_a + ds_b
            df = combined.join(["c", "w"])
            # shared key columns: i, j → inner join on (0, 1) only
            assert len(df) == 1
            assert df.iloc[0]["c"] == 5.0
            assert df.iloc[0]["w"] == 10.0

        def test_join_empty_list_returns_empty(self):
            ds = MultiEntityDataset()
            assert len(ds.join([])) == 0

    # Representation Tests
    class TestRepresentation:
        def test_str_empty(self):
            s = str(MultiEntityDataset())
            assert "Empty" in s

        def test_str_populated(self):
            ds = MultiEntityDataset()
            ds.add_entity("c", ["i"], {(0,): 1})
            s = str(ds)
            assert "c" in s
            assert "1" in s  # record count

        def test_repr(self):
            ds = MultiEntityDataset()
            ds.add_entity("c", ["i"], {(0,): 1})
            assert "c" in repr(ds)