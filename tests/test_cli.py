from account_codes_jp.cli import app


def test_list() -> None:
    """The help message includes the CLI name."""
    app(["list", "--type", "blue-return"])
