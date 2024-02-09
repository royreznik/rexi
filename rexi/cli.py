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
            "--input", "-i",
            help="Input file to pass to rexi; if not provided, stdin will be used.",
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
    app: RexiApp[int] = RexiApp(input_text)
    app.run()
