from click.testing import CliRunner

from account_codes_jp.cli import app

runner = CliRunner()


def test_list() -> None:
    """The help message includes the CLI name."""
    app("list")
