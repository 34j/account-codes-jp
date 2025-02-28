from pathlib import Path

import networkx as nx
from yaml import safe_load


def get_blue_return_accounts_as_graph() -> nx.DiGraph:
    """
    Get the blue return accounts as a graph

    Returns
    -------
    nx.DiGraph
        Tree representation of the blue return account list

    """
    with (Path(__file__).parent / "_blue_return.yaml").open(encoding="utf-8") as f:
        d = safe_load(f)
    G = nx.DiGraph(d)
    for n in G.nodes:
        G.nodes[n]["abstract"] = False
        G.nodes[n]["title"] = False
        G.nodes[n]["total"] = False
    return G
