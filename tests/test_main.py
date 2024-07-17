from typer import Typer
from typer.testing import CliRunner


def test_help(app: Typer, runner: CliRunner) -> None:
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Usage: s3-to-s3" in result.stdout
