from bilevelpy.data.core import MultiEntityDataset
from bilevelpy.data.base_processor import EntityProcessor


class DatasetBuilder:
    """Apply [EntityProcessor][bilevelpy.data.base_processor.EntityProcessor] objects in sequence
    to build a [MultiEntityDataset][bilevelpy.data.core.MultiEntityDataset].

    Example:
        ```python
        dataset = (
            DatasetBuilder()
            .pipe(HLPLoader(Dataset.CAB25))
            .pipe(HLPNodeSelector(n_nodes=10))
            .build()
        )
        ```
    """

    def __init__(self) -> None:
        """Create an empty builder with no processors."""
        self._dataset = MultiEntityDataset()
        self._processors: list[EntityProcessor] = []

    def pipe(self, processor: EntityProcessor) -> "DatasetBuilder":
        """Append a processor to the pipeline.

        Args:
            processor: An [EntityProcessor][bilevelpy.data.base_processor.EntityProcessor] that transforms the dataset.

        Returns:
            ``self``, for method chaining.
        """
        self._processors.append(processor)
        return self

    def build(self) -> MultiEntityDataset:
        """Run all processors in order and return the final dataset.

        Returns:
            The fully processed [MultiEntityDataset][bilevelpy.data.core.MultiEntityDataset].
        """
        for proc in self._processors:
            proc.process(self._dataset)
        return self._dataset