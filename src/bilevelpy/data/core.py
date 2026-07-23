from collections import defaultdict
from typing import Dict, List, Tuple, Any, Iterable


class EntityStore:
    """Handles a specific mathematical mapping from tuples to a single scalar value.

    Args:
        name: Entity name (e.g. ``"c"`` for cost).
        keys: Dimension column names (e.g. ``["fromnode", "tonode"]``).
        data_map: Dictionary mapping tuples to scalar values.
    """

    def __init__(self, name: str, keys: List[str], data_map: Dict[Tuple, Any]):
        self.name = name
        self.keys = keys
        self._prefix_map = defaultdict(list)
        self._data = {}

        self.set_data(data_map)

    def set_data(self, data_map: Dict[Tuple, Any]):
        self._prefix_map.clear()
        self._data = data_map
        for k_tuple in self._data.keys():
            # Safety Check: Enforce tuples to prevent len() checking an integer/string
            if not isinstance(k_tuple, tuple):
                raise TypeError(f"Keys in data_map must be tuples. "
                                f"Found: {type(k_tuple)} for {k_tuple}")

            # Basic validation: does the tuple match the expected key length?
            if len(k_tuple) != len(self.keys):
                raise ValueError(f"Key {k_tuple} length doesn't match expected keys {self.keys}")

            for length in range(1, len(k_tuple)):
                self._prefix_map[k_tuple[:length]].append(k_tuple)

    def to_dataframe(self) -> "pd.DataFrame":
        """Converts the entity's mapping back into a pandas DataFrame."""
        import pandas as pd

        if not self._data:
            # Handling empty data
            return pd.DataFrame(columns=self.keys + [self.name])

        df = pd.Series(self._data).reset_index()

        df.columns = self.keys + [self.name]

        return df

    def find_by_value(self, target_value: Any) -> List[Tuple]:
        """
        Returns all keys that map to the specified value.
        Example: store.find_by_value((0, 1)) -> [(0,), (1,), (2,)]
        """
        return [k for k, v in self._data.items() if v == target_value]

    def items(self) -> Iterable[Tuple[Tuple, Any]]:
        """Allows: for (i, j), cost in store.items():"""
        return self._data.items()


    @property
    def values(self) -> Iterable[Any]:
        return self._data.values()

    def __getitem__(self, key_tuple: Any) -> Any:
        """Fetch value: dataset[DataCol.COST][i, j] -> returns 0.45"""
        k = key_tuple if isinstance(key_tuple, tuple) else (key_tuple,)
        try:
            return self._data[k]
        except KeyError:
            raise KeyError(f"Key {k} not found in entity '{self.name}'")

    def __call__(self, *parent_keys) -> Dict[Tuple, Any]:
        """Filter mapping: dataset[DataCol.COST](i) -> {(i, j): 0.45, ...}"""
        if not parent_keys:
            return self._data

        filtered_keys = self._prefix_map.get(parent_keys, [])
        return {k: self._data[k] for k in filtered_keys}

    def __iter__(self) -> Iterable[Tuple]:
        """Allows iterating keys: for i, j in dataset[DataCol.COST]:"""
        return iter(self._data.keys())

    def __len__(self) -> int:
        """Allows: len(dataset[DataCol.COST])"""
        return len(self._data)

    def __contains__(self, key_tuple: Any) -> bool:
        """Allows: if (i, j) in dataset[DataCol.COST]:"""
        k = key_tuple if isinstance(key_tuple, tuple) else (key_tuple,)
        return k in self._data

    def __str__(self) -> str:
        """Readable string representation."""
        return f"EntityStore(name='{self.name}', keys={self.keys}, size={len(self)})"

    def __repr__(self) -> str:
        """Detailed representation for debugging"""
        return self.__str__()

    @property
    def data(self):
        return self._data

    def is_equal(self, other: 'EntityStore',
                                 use_numpy: bool = True,
                                 epsilon: float = 1e-8,
                                 compare_fn=None) -> bool:
        """Compare this EntityStore with another.

        Args:
            other: another EntityStore to compare against.
            use_numpy: if True, attempt numerical comparison using numpy.isclose / allclose
            epsilon: numerical tolerance when use_numpy is True.
            compare_fn: optional callable(a, b) -> bool used to determine equality for each value.

        Returns:
            True if the two EntityStore instances are considered equal, False otherwise.
        """
        # Basic type check
        if not isinstance(other, EntityStore):
            return False

        # Dimensionality checks: same declared keys (names) and same mapping size
        if len(self.keys) != len(other.keys):
            return False

        # Check that the set of mapping keys is identical
        if set(self._data.keys()) != set(other._data.keys()):
            return False

        # Helper comparison function
        def _values_equal(a, b) -> bool:
            # If custom comparator provided, use it
            if compare_fn is not None:
                try:
                    return bool(compare_fn(a, b))
                except Exception:
                    return False

            # If numpy-based numerical comparison requested
            if use_numpy:
                try:
                    import numpy as _np

                    # If both are scalar (int/float/complex)
                    if isinstance(a, (int, float, complex)) and isinstance(b, (int, float, complex)):
                        return bool(_np.isclose(a, b, atol=epsilon, rtol=0))

                    # If either is array-like / sequence, try converting to numpy arrays
                    # This will also handle tuples/lists of numbers
                    a_arr = _np.asarray(a)
                    b_arr = _np.asarray(b)

                    # If shapes are not compatible, not equal
                    if a_arr.shape != b_arr.shape:
                        return False

                    # Use allclose for elementwise comparison, allow NaNs in same positions
                    return bool(_np.allclose(a_arr, b_arr, atol=epsilon, rtol=0, equal_nan=True))
                except Exception:
                    # Fall back to plain equality if numpy not available or conversion fails
                    return a == b

            # Default: Python equality
            return a == b

        # Compare every mapped entry
        for k in self._data.keys():
            if k not in other._data:
                return False

            v1 = self._data[k]
            v2 = other._data[k]

            if not _values_equal(v1, v2):
                return False

        return True

    def __eq__(self, other: object) -> bool:
        """Equality operator uses numerical-aware comparison by default."""
        if not isinstance(other, EntityStore):
            return NotImplemented
        return self.is_equal(other, use_numpy=True)


class MultiEntityDataset:
    """Collection of named EntityStore instances."""

    def __init__(self):
        self._stores: Dict[str, EntityStore] = {}

    def add_entity(self, name: str, keys: List[str], data_map: Dict[Tuple, Any]) -> None:
        self._stores[name] = EntityStore(name, keys, data_map)

    def join(self, names: List[str], how: str = "inner") -> "pd.DataFrame":
        """
        Relational join across selected entities.
        """
        import pandas as pd

        # Generator expression for lazy DataFrame creation
        dfs = (self._stores[n].to_dataframe() for n in names if n in self._stores)

        try:
            first_df = next(dfs)
        except StopIteration:
            return pd.DataFrame()

        result = first_df
        for next_df in dfs:
            # Join on the intersection of columns (automatic key discovery)
            common = list(set(result.columns) & set(next_df.columns))
            # Filter out the actual variable names from the join keys
            join_keys = [c for c in common if c not in names]
            result = result.merge(next_df, on=join_keys, how=how)

        return result

    def __add__(self, other: 'MultiEntityDataset') -> 'MultiEntityDataset':
        """
        Allows: combined = dataset_a + dataset_b
        Returns a NEW MultiEntityDataset containing entities from both.
        """
        if not isinstance(other, MultiEntityDataset):
            return NotImplemented

        new_dataset = MultiEntityDataset()

        new_store = self._stores.copy()
        new_store.update(other._stores.copy())

        new_dataset._stores = new_store
        return new_dataset

    def __getitem__(self, entity_name: str) -> EntityStore:
        if entity_name not in self._stores:
            raise KeyError(f"Entity '{entity_name}' not found. Available: {list(self._stores.keys())}")
        return self._stores[entity_name]

    def __iter__(self):
        """Allows iterating over entity names: for name in dataset:"""
        return iter(self._stores.keys())

    def __len__(self) -> int:
        """Allows: len(dataset) -> returns number of entities."""
        return len(self._stores)

    def __contains__(self, entity_name: str) -> bool:
        """Allows: if 'cost' in dataset:"""
        return entity_name in self._stores

    def __str__(self) -> str:
        """Multi-line overview of all entities."""
        if not self._stores:
            return "MultiEntityDataset (Empty)"

        lines = [f"MultiEntityDataset with {len(self)} entities:"]
        for name, store in self._stores.items():
            lines.append(f"  - [{name}]: {len(store)} records mapped by {store.keys}")
        return "\n".join(lines)

    def __repr__(self) -> str:
        """Console representation."""
        return f"MultiEntityDataset(entities={list(self._stores.keys())})"