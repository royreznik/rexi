from io import BytesIO
from pathlib import Path
from unittest.mock import Mock

from _pytest.monkeypatch import MonkeyPatch
from typer.testing import CliRunner
from rexi.cli import app


def test_on_args(monkeypatch: MonkeyPatch) -> None:
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
    class_mock.assert_called_once_with(
        text.decode(), initial_mode=None, initial_pattern=None
    )
    instance_mock.run.assert_called_once()


def test_file_input(monkeypatch: MonkeyPatch, tmp_path: Path) -> None:
    runner = CliRunner()
    text = "This iS! aTe xt2 F0r T3sT!ng"
    (tmp_path / "text_file").write_text(text)
    class_mock = Mock()
    instance_mock = Mock()
    with monkeypatch.context():
        class_mock.return_value = instance_mock
        monkeypatch.setattr("rexi.cli.RexiApp", class_mock)
        runner.invoke(app, args=["-i", str(tmp_path / "text_file")])
    class_mock.assert_called_once_with(text, initial_mode=None, initial_pattern=None)


def test_initial_pattern(monkeypatch: MonkeyPatch, tmp_path: Path) -> None:
    runner = CliRunner()
    text = "This iS! aTe xt2 F0r T3sT!ng"
    (tmp_path / "text_file").write_text(text)
    class_mock = Mock()
    instance_mock = Mock()
    with monkeypatch.context():
        class_mock.return_value = instance_mock
        monkeypatch.setattr("rexi.cli.RexiApp", class_mock)
        runner.invoke(app, args=["-i", str(tmp_path / "text_file"), "--pattern", "wtf"])
    class_mock.assert_called_once_with(text, initial_mode=None, initial_pattern="wtf")


def test_initial_mode(monkeypatch: MonkeyPatch, tmp_path: Path) -> None:
    runner = CliRunner()
    text = "This iS! aTe xt2 F0r T3sT!ng"
    (tmp_path / "text_file").write_text(text)
    class_mock = Mock()
    instance_mock = Mock()
    with monkeypatch.context():
        class_mock.return_value = instance_mock
        monkeypatch.setattr("rexi.cli.RexiApp", class_mock)
        runner.invoke(app, args=["-i", str(tmp_path / "text_file"), "--mode", "match"])
    class_mock.assert_called_once_with(text, initial_mode="match", initial_pattern=None)
