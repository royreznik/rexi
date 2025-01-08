import os
from io import BytesIO
from pathlib import Path
from typing import Any
from unittest.mock import Mock

import pytest
from _pytest.monkeypatch import MonkeyPatch
from typer.testing import CliRunner

from rexi.cli import app, is_stdin_a_tty


@pytest.mark.parametrize("input_value", [True, False])
def test_is_stdin_a_tty(monkeypatch: MonkeyPatch, input_value: bool) -> None:
    isatty_mock = Mock()
    with monkeypatch.context():
        isatty_mock.return_value = input_value
        monkeypatch.setattr("rexi.cli.sys.stdin.isatty", isatty_mock)
        assert is_stdin_a_tty() == input_value


def test_no_args(monkeypatch: MonkeyPatch) -> None:
    runner = CliRunner()
    class_mock = Mock()
    instance_mock = Mock()
    with monkeypatch.context():
        class_mock.return_value = instance_mock
        monkeypatch.setattr("rexi.cli.RexiApp", class_mock)
        result = runner.invoke(app)

    assert result.exit_code == 0
    class_mock.assert_called_once_with("", initial_mode=None, initial_pattern=None)


def test_string_input(monkeypatch: MonkeyPatch) -> None:
    runner = CliRunner()
    text = "This iS! aTe xt2 F0r T3sT!ng"
    class_mock = Mock()
    instance_mock = Mock()
    with monkeypatch.context():
        class_mock.return_value = instance_mock
        monkeypatch.setattr("rexi.cli.is_stdin_a_tty", lambda: True)
        monkeypatch.setattr("rexi.cli.RexiApp", class_mock)
        result = runner.invoke(app, args=[text])

    assert result.exit_code == 0
    class_mock.assert_called_once_with(text, initial_mode=None, initial_pattern=None)


def test_stdin_input(monkeypatch: MonkeyPatch) -> None:
    """
    Couldn't find a better way to test the CLI without patching everything :(
    """
    runner = CliRunner()
    text = b"This iS! aTe xt2 F0r T3sT!ng"
    a = BytesIO(text)
    class_mock = Mock()
    instance_mock = Mock()
    open_mock = Mock()
    read_mock = Mock()

    with monkeypatch.context():
        read_mock.return_value = ""
        class_mock.return_value = instance_mock
        monkeypatch.setattr("rexi.cli.is_stdin_a_tty", lambda: False)
        monkeypatch.setattr("rexi.cli.RexiApp", class_mock)
        monkeypatch.setattr("builtins.open", open_mock)
        result = runner.invoke(app, input=a)
        open_mock.assert_called_once_with(
            "con:" if os.name == "nt" else "/dev/tty", "rb"
        )

    assert result.exit_code == 0
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
        monkeypatch.setattr("rexi.cli.is_stdin_a_tty", lambda: True)
        result = runner.invoke(app, args=["-i", str(tmp_path / "text_file")])

    assert result.exit_code == 0
    class_mock.assert_called_once_with(text, initial_mode=None, initial_pattern=None)


@pytest.mark.parametrize("use_stdin", [False, True])
@pytest.mark.parametrize("use_input", [False, True])
@pytest.mark.parametrize("use_string", [False, True])
def test_argument_conflicts(
    monkeypatch: MonkeyPatch,
    tmp_path: Path,
    use_stdin: bool,
    use_input: bool,
    use_string: bool,
) -> None:
    """
    Couldn't find a better way to test the CLI without patching everything :(
    """
    # Text stdin
    text_stdin = "stdin: This iS! aTe xt2 F0r T3sT!ng"
    a = BytesIO(text_stdin.encode())
    # Text string
    text_string = "string: ThaT iS! éhé"
    # Text input file
    text_input = "input: This iS! aTe xt2 F0r T3sT!ng"
    tmp_file = tmp_path / "text_file"
    tmp_file.write_text(text_input)

    # Initialize mocks
    runner = CliRunner()
    class_mock = Mock()
    instance_mock = Mock()
    read_mock = Mock()

    with monkeypatch.context():
        read_mock.return_value = ""
        monkeypatch.setattr("rexi.cli.is_stdin_a_tty", lambda: not use_stdin)
        monkeypatch.setattr("rexi.cli.RexiApp", class_mock)
        class_mock.return_value = instance_mock

        kwargs: dict[str, Any] = {}
        args = []
        if use_stdin:
            kwargs["input"] = a
        if use_input:
            args.extend(["-i", os.fspath(tmp_file)])
        if use_string:
            args.extend([text_string])
        if args:
            kwargs["args"] = args
        # Call CLI
        result = runner.invoke(app, **kwargs)

    # Check result
    has_conflict = int(use_stdin + use_string + use_input) > 1
    if has_conflict:
        assert result.exit_code > 0
        assert "Invalid value" in result.output
        return

    expected_text = ""
    if use_stdin:
        expected_text = text_stdin
    elif use_input:
        expected_text = text_input
    elif use_string:
        expected_text = text_string

    assert result.exit_code == 0
    class_mock.assert_called_once_with(
        expected_text,
        initial_mode=None,
        initial_pattern=None,
    )
    instance_mock.run.assert_called_once()


def test_initial_pattern(monkeypatch: MonkeyPatch, tmp_path: Path) -> None:
    runner = CliRunner()
    text = "This iS! aTe xt2 F0r T3sT!ng"
    class_mock = Mock()
    instance_mock = Mock()
    with monkeypatch.context():
        class_mock.return_value = instance_mock
        monkeypatch.setattr("rexi.cli.is_stdin_a_tty", lambda: True)
        monkeypatch.setattr("rexi.cli.RexiApp", class_mock)
        runner.invoke(app, args=[text, "--pattern", "wtf"])
    class_mock.assert_called_once_with(text, initial_mode=None, initial_pattern="wtf")


def test_initial_mode(monkeypatch: MonkeyPatch, tmp_path: Path) -> None:
    runner = CliRunner()
    text = "This iS! aTe xt2 F0r T3sT!ng"
    class_mock = Mock()
    instance_mock = Mock()
    with monkeypatch.context():
        class_mock.return_value = instance_mock
        monkeypatch.setattr("rexi.cli.is_stdin_a_tty", lambda: True)
        monkeypatch.setattr("rexi.cli.RexiApp", class_mock)
        runner.invoke(app, args=[text, "--mode", "match"])
    class_mock.assert_called_once_with(text, initial_mode="match", initial_pattern=None)
