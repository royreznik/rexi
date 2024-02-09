import os
import sys
from typing import Annotated, Optional

import typer

from .rexi import RexiApp

app = typer.Typer()


# noinspection SpellCheckingInspection
@app.command("rexi")
def rexi_cli(
    input_file: Annotated[
        Optional[typer.FileText],
        typer.Option(
            "--input",
            "-i",
            help="Input file to pass to rexi; if not provided, stdin will be used.",
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
    if input_file:
        input_text = input_file.read()
    else:
        input_text = sys.stdin.read()
        try:
            os.close(sys.stdin.fileno())
        except OSError:
            pass
        sys.stdin = open("/dev/tty", "rb")  # type: ignore[assignment]
    app: RexiApp[int] = RexiApp(
        input_text, initial_mode=initial_mode, initial_pattern=initial_pattern
    )
    app.run()
