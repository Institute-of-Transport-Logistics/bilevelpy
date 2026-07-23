import random
from typing import Set, Dict, Tuple, Any

from bilevelpy.data.base_processor import EntityProcessor
from bilevelpy.data.core import MultiEntityDataset
from bilevelpy.core.columns import  DataCol

class HLPNodeSelector(EntityProcessor):
    """Subsample a dataset to a smaller number of nodes.

    Filters every [EntityStore][bilevelpy.data.core.EntityStore] in the dataset
    to only include entries whose tuple keys are subsets of the selected
    nodes.

    Args:
        n_nodes: Number of nodes to retain.
        random_nodes: If ``True``, sample randomly. Otherwise take the
            first ``n_nodes`` in sorted order.
        seed: Random seed for reproducibility.
    """

    def __init__(
        self,
        n_nodes: int,
        random_nodes: bool = False,
        seed: int = 42,
    ):
        self.n_nodes = n_nodes
        self.random_nodes = random_nodes
        self.random_obj = random.Random(seed)

    def process(self, dataset: MultiEntityDataset) -> None:
        """Subsample nodes and filter all entities.

        Args:
            dataset: The dataset to subsample (modified in-place).

        Raises:
            ValueError: If ``n_nodes`` exceeds the number of available nodes.
            AttributeError: If required entities are missing.
        """
        self.__check_dataset(dataset)
        sampled_nodes = self.__sample_nodes(dataset)

        for entity_name in list(dataset):
            entity = dataset[entity_name]
            filtered_data_map: Dict[Tuple, Any] = {}
            for keys, values in entity.items():
                if all(k in sampled_nodes for k in keys):
                    filtered_data_map[keys] = values
            entity.set_data(filtered_data_map)

    def __sample_nodes(self, dataset: MultiEntityDataset) -> Set:
        node_ids = dataset[DataCol.NODE_ID]
        all_nodes = [node_ids[key] for key in node_ids]

        if self.n_nodes > len(all_nodes):
            raise ValueError(f"Requested {self.n_nodes} nodes, "
                             f"but only {len(all_nodes)} available.")

        if self.random_nodes:
            selected_nodes = set(self.random_obj.sample(all_nodes,
                                                                                        self.n_nodes))
        else:
            selected_nodes = set(sorted(all_nodes)[:self.n_nodes])
        return selected_nodes

    def __check_dataset(self, dataset: MultiEntityDataset):
        if DataCol.NODE_ID not in dataset:
            raise AttributeError(f"{DataCol.NODE_ID.value} not found in dataset.")

        if DataCol.COST_NODE_TO_NODE not in dataset:
            raise AttributeError(f"{DataCol.COST_NODE_TO_NODE.value} not found in dataset.")

class HLPCostScaling(EntityProcessor):
    """Scale transport costs by a constant factor.

    Args:
        scaling_factor: Divisor applied to every cost value
            (e.g., ``100.0`` divides all costs by 100).
    """

    def __init__(self, scaling_factor: float):
        self.scaling_factor = scaling_factor

    def process(self, dataset: MultiEntityDataset) -> None:
        """Divide all cost values by the scaling factor.

        Args:
            dataset: Dataset to transform (modified in-place).

        Raises:
            AttributeError: If ``DataCol.COST_NODE_TO_NODE`` is missing.
        """
        if DataCol.COST_NODE_TO_NODE not in dataset:
            raise AttributeError(f"{DataCol.COST_NODE_TO_NODE.value}"
                                 f" not found in dataset.")

        cost_store = dataset[DataCol.COST_NODE_TO_NODE]

        scaled_map = {
            keys: value / self.scaling_factor
            for keys, value in cost_store.items()
        }

        cost_store.set_data(scaled_map)
