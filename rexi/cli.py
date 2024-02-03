import os
import sys

import typer

from .rexi import RexiApp

app = typer.Typer()


# noinspection SpellCheckingInspection
@app.command("rexi")
def rexi_cli() -> None:
    stdin = sys.stdin.read()
    try:
        os.close(sys.stdin.fileno())
    except OSError:
        pass
    sys.stdin = open("/dev/tty", "rb")  # type: ignore[assignment]
    app: RexiApp[int] = RexiApp(stdin)
    app.run()
