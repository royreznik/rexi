import os
import select
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
        """
        Yep this part is abit ugly.
        couldn't find a better way to implement it so it will work with `typer`, `pytest` and `textual`
        """  # noqa: E501
        if not select.select(
            [
                sys.stdin,
            ],
            [],
            [],
            0.0,
        )[0]:
            raise typer.BadParameter(
                "stdin is empty, "
                "please provide text thru the stdin "
                "or use the `-i` flag"
            )
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
