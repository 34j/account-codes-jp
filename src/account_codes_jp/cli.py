import networkx as nx
import typer

from ._main import get_all_account

app = typer.Typer()


@app.command()
def list() -> None:
    """List accounts."""
    df, G = get_all_account()
    nx.write_network_text(G, with_labels=True, max_depth=20)
