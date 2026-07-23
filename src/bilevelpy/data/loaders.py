import importlib.resources
import math
import pandas as pd


from bilevelpy.data.base_processor import EntityProcessor
from bilevelpy.data.core import MultiEntityDataset
from bilevelpy.core.datasets import Dataset
from bilevelpy.core.columns import DataCol

class HLPLoader(EntityProcessor):
    """Load CAB dataset files into a [MultiEntityDataset][bilevelpy.data.core.MultiEntityDataset]."""

    def __init__(self, dataset: Dataset = Dataset.CAB25):
        self._dataset = dataset
        self._resource = (
            importlib.resources.files("bilevelpy.data") / "datasets" / self._dataset.value
        )
        if not self._resource.is_file():
            raise FileNotFoundError(
                f"Dataset file not found: {self._dataset.value}\n"
                f"Check if the file exists in the bilevelpy/data/datasets/ directory."
            )

    def process(self, dataset_container: 'MultiEntityDataset') -> None:
        """Executes the loading logic and populates the MultiEntityDataset."""
        if self._dataset in [Dataset.CAB25, Dataset.CAB100]:
            df = self.__load_cab()
        else:
            raise AttributeError(f"Loading logic for {self._dataset} not implemented.")

        # TODO: add correct support to the TR Dataset
        # TODO: add correct support to the USA423 dataset
        cost_map = df.set_index([DataCol.START_NODE,
                                 DataCol.END_NODE])[DataCol.COST_NODE_TO_NODE].to_dict()

        dataset_container.add_entity(
            name=DataCol.COST_NODE_TO_NODE,
            keys=[DataCol.START_NODE, DataCol.END_NODE],
            data_map= cost_map
        )

        weight_map = df.set_index([DataCol.START_NODE,
                                 DataCol.END_NODE])[DataCol.WEIGHTS_NODE_TO_NODE].to_dict()

        dataset_container.add_entity(
            name=DataCol.WEIGHTS_NODE_TO_NODE,
            keys=[DataCol.START_NODE, DataCol.END_NODE],
            data_map= weight_map
        )

        unique_nodes = sorted(df[DataCol.START_NODE].unique())

        nodes_map = {(n,): n for n in unique_nodes}
        dataset_container.add_entity(
            name=DataCol.NODE_ID,
            keys=[DataCol.NODE_ID],
            data_map= nodes_map
        )

    def __load_cab(self) -> pd.DataFrame:
        """Internal CAB parser logic."""
        with importlib.resources.as_file(self._resource) as path:
            with open(path, "r") as file:
                data = [line.split() for line in file.read().strip().split("\n")]

        df = pd.DataFrame(data, columns=[
            DataCol.START_NODE,
            DataCol.END_NODE,
            DataCol.WEIGHTS_NODE_TO_NODE,
            DataCol.COST_NODE_TO_NODE,
        ])

        # Formatting values
        df[DataCol.START_NODE] = df[DataCol.START_NODE].astype(int) - 1
        df[DataCol.END_NODE] = df[DataCol.END_NODE].astype(int) - 1
        df[DataCol.WEIGHTS_NODE_TO_NODE] = df[DataCol.WEIGHTS_NODE_TO_NODE].astype(float)
        df[DataCol.COST_NODE_TO_NODE] = df[DataCol.COST_NODE_TO_NODE].astype(float)

        return df




