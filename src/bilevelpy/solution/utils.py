"""Utility functions for Gurobi solution parsing."""

import re


def extract_gurobi_name(var_name_str: str) -> tuple[str, tuple[int, ...]]:
    """Parse a Gurobi variable name into its base name and index tuple.

    Gurobi names variables like ``x[0,1]``, ``y(2,3,5)``, or ``p_0_1``.
    This function extracts the base name and the integer indices.

    Args:
        var_name_str: Raw Gurobi variable name (e.g. ``"x[3,7]"``).

    Returns:
        A ``(name, indices)`` tuple. ``name`` is the base string
        (e.g. ``"x"``), ``indices`` is a tuple of ints (e.g. ``(3, 7)``).
        If no indices are found, returns ``(var_name_str, ())``.
    """
    match = re.search(r"\[|\(|_(?=\d)", var_name_str)

    if match:
        split_index = match.start()
        name_part = var_name_str[:split_index]
        indices_part = var_name_str[split_index:]
    else:
        return var_name_str, ()

    name_part = name_part.rstrip("_")
    indices_list = re.findall(r"-?\d+", indices_part)

    return name_part, tuple(int(x) for x in indices_list)
