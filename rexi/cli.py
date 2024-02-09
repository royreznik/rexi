import os
import sys
from typing import Annotated, Optional

import typer

from .rexi import RexiApp

app = typer.Typer()


# noinspection SpellCheckingInspection
@app.command("rexi")
def rexi_cli(
    input_file: Optional[Annotated[
        typer.FileText,
        typer.Option(
            "-i",
            "--input",
            rich_help_panel="Input file to pass to rexi; if not provided, stdin will be used.",
        ),
    ]] = None,
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
