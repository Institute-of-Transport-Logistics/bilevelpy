
from abc import ABC, abstractmethod

from bilevelpy.data.core import MultiEntityDataset

class EntityProcessor(ABC):
    """Base class for anything that adds 'computed columns' to a dataset."""
    @abstractmethod
    def process(self, dataset: MultiEntityDataset) -> None:
        """Logic to modify the dataset goes here."""
        pass