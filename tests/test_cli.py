from io import BytesIO
from unittest.mock import Mock

from _pytest.monkeypatch import MonkeyPatch
from typer.testing import CliRunner
from rexi.cli import app


def test_app(monkeypatch: MonkeyPatch) -> None:
    """
    Couldn't find a better way to test the CLI without patching everything :(
    """
    runner = CliRunner()
    text = b"This iS! aTe xt2 F0r T3sT!ng"
    a = BytesIO(text)
    class_mock = Mock()
    instance_mock = Mock()
    open_mock = Mock()
    with monkeypatch.context():
        class_mock.return_value = instance_mock
        monkeypatch.setattr("rexi.cli.RexiApp", class_mock)
        monkeypatch.setattr("builtins.open", open_mock)
        runner.invoke(app, input=a)
    open_mock.assert_called_once_with("/dev/tty", "rb")
    class_mock.assert_called_once_with(text.decode())
    instance_mock.run.assert_called_once()
