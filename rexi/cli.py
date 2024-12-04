import os
import sys
from typing import Annotated, Optional

import typer

from .rexi import RexiApp

app = typer.Typer()


def is_stdin_a_tty() -> bool:
    """Wrapper for sys.stdin.isatty.

    Trying to directly mock/patch sys.stdin.isatty wasn't working,
    but it's easy to patch a function that calls sys.stdin.isatty()
    """
    return sys.stdin.isatty()


# noinspection SpellCheckingInspection
@app.command("rexi")
def rexi_cli(
    text: Annotated[
        Optional[str],
        typer.Argument(
            help="String to pass to rexi; if not provided, stdin will be used.",
        ),
    ] = None,
    input_file: Annotated[
        Optional[typer.FileText],
        typer.Option(
            "--input",
            "-i",
            help="Input file to pass to rexi; if used, TEXT should be empty.",
        ),
    ] = None,
    initial_pattern: Annotated[
        Optional[str],
        typer.Option(
            "--pattern",
            "-p",
            help="Initial regex pattern to use",
        ),
    ] = None,
    initial_mode: Annotated[
        Optional[str],
        typer.Option(
            "--mode",
            "-m",
            help="Initial regex mode to use",
        ),
    ] = None,
) -> None:
    """Try regex patterns on a string.

    If `--input FILE` is used, read the file content.
    """
    # Input file provided
    if input_file:
        # Incompatible with a string argument
        if text:
            msg = (
                "TEXT argument should be empty if in input is provided with "
                "the `-i` flag."
            )
            raise typer.BadParameter(msg)

        input_text = input_file.read()

    # Read stdin
    elif not is_stdin_a_tty():
        input_text = sys.stdin.read()
        try:
            os.close(sys.stdin.fileno())
        except OSError:
            pass
        # Windows uses "con:" for stdin device name
        sys.stdin = open("con:" if os.name == "nt" else "/dev/tty", "rb")  # type: ignore[assignment]

        # Incompatible with a string argument
        if text:
            msg = "TEXT argument should be empty if text is piped through stdin."
            raise typer.BadParameter(msg)

    # Input string provided or fallback to empty string
    else:
        input_text = text or ""

    app: RexiApp[int] = RexiApp(
        input_text,
        initial_mode=initial_mode,
        initial_pattern=initial_pattern,
    )
    app.run()
    print(app.pattern)
