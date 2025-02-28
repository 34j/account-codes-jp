from pathlib import Path

import cyclopts
from networkx.readwrite.text import generate_network_text
from rich import print

from ._main import Industry, etax_account_as_graph, get_etax_accounts

app = cyclopts.App(name="account-codes-jp")


@app.command()
def list(industry: Industry | None = None) -> None:
    """List accounts."""
    df = get_etax_accounts(industry)
    # set red
    df.loc[df["abstract"] == True, "label"] = (
        "[italic]" + df["label"] + "[/italic][抽象]"
    )
    df.loc[df["title"] == True, "label"] = "[red]" + df["label"] + "[/red][タイトル]"
    df.loc[df["total"] == True, "label"] = "[yellow]" + df["label"] + "[/yellow][計]"
    df.loc[df["duration"] == True, "label"] = df["label"] + "[期間]"
    G = etax_account_as_graph(df)
    for line in generate_network_text(G, with_labels=True, max_depth=20):
        print(line)


def export(path: Path, industry: Industry | None = None) -> None:
    """Export accounts."""
    df = get_etax_accounts(industry)
    df.to_csv(path, index=False)
