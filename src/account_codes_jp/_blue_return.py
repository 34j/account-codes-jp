from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

import networkx as nx
from yaml import safe_load


def from_nested_dict(
    data: Mapping[Any, Mapping[Any, Any] | Sequence[Any]],
) -> nx.DiGraph:
    """
    Convert a nested mapping of mappings and sequences to a directed graph.

    Parameters
    ----------
    data : Mapping[Any, Mapping[Any, Any] | Sequence[Any]]
        Nested dictionary

    Returns
    -------
    nx.DiGraph
        Directed graph

    """
    G = nx.DiGraph()
    q: list[tuple[Any, Any]] = [(None, data)]
    id_child = 0
    while q:
        id_parent, d = q.pop()
        for k_child, grandchildren in d.items():
            id_child += 1
            G.add_node(id_child, label=k_child)
            if id_parent is not None:
                G.add_edge(id_parent, id_child)
            if isinstance(grandchildren, Mapping):
                q.append((id_child, grandchildren))
            elif isinstance(grandchildren, list):
                q.append((id_child, {k: None for k in grandchildren}))
    return G


def get_blue_return_accounts() -> nx.DiGraph:
    """
    Get the blue return accounts as a graph

    Returns
    -------
    nx.DiGraph
        Tree representation of the blue return account list

    """
    with (Path(__file__).parent / "_blue_return.yaml").open(encoding="utf-8") as f:
        d = safe_load(f)
    G = from_nested_dict(d)
    root = next(iter(nx.topological_sort(G)))
    for n in G.nodes:
        ancestors = nx.shortest_path(G, root, n)
        depth = len(ancestors)
        G.nodes[n]["ancestors"] = ancestors
        G.nodes[n]["abstract"] = depth <= 2
        G.nodes[n]["title"] = depth <= 2
        G.nodes[n]["total"] = False
        if len(ancestors) > 2:
            G.nodes[n]["debit"] = ancestors[1] in ["資産", "費用"]
            G.nodes[n]["static"] = ancestors[1] in ["資産", "純資産", "負債"]
            G.nodes[n]["account_type"] = ancestors[1]
        else:
            G.nodes[n]["debit"] = None
            G.nodes[n]["static"] = None
            G.nodes[n]["account_type"] = None
    return G
