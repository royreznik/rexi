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
    elif not is_stdin_a_tty():
        input_text = sys.stdin.read()
        # Reopen stdin from the console device so Textual can read
        # interactive input (keyboard + mouse events).
        # We must place it on fd 0 so that Textual's low-level input
        # reader sees the console, not the closed pipe.
        console_device = "CONIN$" if os.name == "nt" else "/dev/tty"
        try:
            os.close(sys.stdin.fileno())
        except OSError:
            pass
        new_fd = os.open(console_device, os.O_RDONLY)
        if new_fd != 0:
            os.dup2(new_fd, 0)
            os.close(new_fd)
        sys.stdin = os.fdopen(0, "r", closefd=False)  # type: ignore[assignment]
    else:
        raise typer.BadParameter(
            "stdin is empty, "
            "please provide text thru the stdin "
            "or use the `-i` flag"
        )
    app: RexiApp[int] = RexiApp(
        input_text, initial_mode=initial_mode, initial_pattern=initial_pattern
    )
    app.run()
    print(app.pattern)
