from enum import StrEnum


class DataCol(StrEnum):
    r"""Column headers and data identifiers used in datasets and models.

    Attributes:
        X: The X-coordinate of the node.
        Y: The Y-coordinate of the node.
        START_NODE: The starting node, denoted mathematically as $i \in V$.
        END_NODE: The ending node, denoted mathematically as $j \in V$.
        COST_NODE_TO_NODE: The transport cost between two nodes, typically denoted as $c_{ij}$.
        WEIGHTS_NODE_TO_NODE: Weights used in the Hub Location Problem, denoted as $w_{ij}$.
    """

    X = "coordinate_x"

    Y = "coordinate_y"

    NODE_ID = "node_id"

    START_NODE = "fromnode"

    END_NODE = "tonode"

    COST_NODE_TO_NODE = "c"

    WEIGHTS_NODE_TO_NODE = "w"
