from __future__ import annotations

from typing import TYPE_CHECKING

from bilevelpy.core.columns import DataCol

if TYPE_CHECKING:
    from bilevelpy.models import BaseModel


def get_nodes(instance: BaseModel) -> list[str]:
    """Return the list of node IDs from the model's dataset.

    Args:
        instance: The model instance whose data contains node identifiers.

    Returns:
        List of node ID strings (e.g., ``["1", "2", ..., "25"]``).
    """
    return list(instance.data[DataCol.NODE_ID].values)


def transport_cost_hlp(
    instance: BaseModel,
    i: str,
    k: str,
    m: str,
    j: str,
    alpha: float,
) -> float:
    r"""Compute the discounted transport cost through hubs $k$ and $m$.

    $$c_{ik} + \alpha \cdot c_{km} + c_{mj}$$

    where $\alpha \in [0,1]$ is the inter-hub discount factor.

    Args:
        instance: The model containing transport cost data.
        i: Origin node.
        k: First hub.
        m: Second hub.
        j: Destination node.
        alpha: Inter-hub discount factor ($0 \leq \alpha \leq 1$).

    Returns:
        The total transport cost as a float.
    """
    costs = instance.data[DataCol.COST_NODE_TO_NODE]
    return costs[i, k] + alpha * costs[k, m] + costs[m, j]