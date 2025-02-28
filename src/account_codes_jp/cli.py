from logging import basicConfig
from pathlib import Path
from typing import Annotated, Literal

import cyclopts
from cyclopts import Parameter
from networkx.readwrite.text import generate_network_text
from rich import print
from rich.logging import RichHandler

from ._blue_return import get_blue_return_accounts_as_graph
from ._edinet import Industry, etax_accounts_as_graph, get_etax_accounts

app = cyclopts.App(name="account-codes-jp")
app.meta.group_parameters = cyclopts.Group("Session Parameters", sort_key=0)


@app.command
def list(
    type: Literal["edinet", "blue-return"] = "edinet", industry: Industry | None = None
) -> None:
    """List accounts."""
    if type == "edinet":
        df = get_etax_accounts(industry, debug_unique=True)
        G = etax_accounts_as_graph(df)
    elif type == "blue-return":
        G = get_blue_return_accounts_as_graph()
    else:
        raise ValueError(f"Unknown account type: {type}")
    for n, d in G.nodes(data=True):
        if d["abstract"]:
            G.nodes[n]["label"] = "[red]" + d["label"] + "[/red]"
        if d["title"]:
            G.nodes[n]["label"] += "[タイトル]"
        if d["total"]:
            G.nodes[n]["label"] = "[yellow]" + d["label"] + "[/yellow][計]"
        if type == "edinet":
            G.nodes[n]["label"] += (
                "/"
                + "[green]"
                + d["label_etax"]
                + "[/green]"
                + "/[sky_blue3]"
                + d["prefix"]
                + ":"
                + d["element"]
                + "[/sky_blue3]"
            )
    for line in generate_network_text(G, with_labels=True, max_depth=20):
        print(line)


def export(path: Path, industry: Industry | None = None) -> None:
    """Export accounts."""
    df = get_etax_accounts(industry)
    df.to_csv(path, index=False)


@app.meta.default
def _app_launcher(
    *tokens: Annotated[str, Parameter(show=False, allow_leading_hyphen=True)],
    verbose: bool = False,
) -> None:
    basicConfig(level="DEBUG" if verbose else "INFO", handlers=[RichHandler()])
    app(tokens)
