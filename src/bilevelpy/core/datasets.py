from enum import StrEnum


class Dataset(StrEnum):
    r"""Supported datasets in the library

    Attributes:
        CAB25: The CAB dataset containing 25 nodes.
        CAB100: The CAB dataset containing 100 nodes.

    """
    CAB25 = "cab25.txt"
    CAB100 = "cab100.txt"


