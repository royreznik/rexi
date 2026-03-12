import os
import sys
from typing import Annotated, Optional

import typer

from .rexi import RexiApp

app = typer.Typer()


def _reopen_stdin() -> None:
    """Reopen stdin from the console so Textual can read interactive input.

    After reading piped input, stdin points to the exhausted pipe. Textual
    needs a real console for keyboard and mouse events.

    On Linux/macOS, Textual reads from fd 0 (sys.__stdin__.fileno()), so we
    reopen /dev/tty onto fd 0.

    On Windows, Textual uses GetStdHandle(STD_INPUT_HANDLE) which is a
    separate Windows handle — reopening fd 0 alone is not enough. We must
    also call SetStdHandle to point STD_INPUT_HANDLE at a fresh CONIN$ handle.
    """
    if os.name == "nt":
        _reopen_stdin_windows()
    else:
        _reopen_stdin_unix()


def _reopen_stdin_unix() -> None:
    try:
        os.close(sys.stdin.fileno())
    except OSError:
        pass
    new_fd = os.open("/dev/tty", os.O_RDONLY)
    if new_fd != 0:
        os.dup2(new_fd, 0)
        os.close(new_fd)
    new_stdin = os.fdopen(0, "r", closefd=False)
    sys.stdin = new_stdin  # type: ignore[assignment]
    sys.__stdin__ = new_stdin  # type: ignore[assignment]


def _reopen_stdin_windows() -> None:
    import ctypes
    from ctypes import wintypes

    kernel32 = ctypes.windll.kernel32  # type: ignore[attr-defined]
    STD_INPUT_HANDLE = wintypes.DWORD(-10)
    GENERIC_READ_WRITE = wintypes.DWORD(0x80000000 | 0x40000000)
    FILE_SHARE_READ_WRITE = wintypes.DWORD(0x00000001 | 0x00000002)
    OPEN_EXISTING = wintypes.DWORD(3)

    # Open a fresh handle to the console input buffer.
    # Textual's win32.EventMonitor calls GetStdHandle(STD_INPUT_HANDLE)
    # then ReadConsoleInputW on it, so we need to redirect that handle.
    # Textual's enable_application_mode() also calls
    # msvcrt.get_osfhandle(sys.__stdin__.fileno()) to set console mode
    # (including ENABLE_VIRTUAL_TERMINAL_INPUT for mouse), so we must
    # fix sys.__stdin__ as well.
    handle = kernel32.CreateFileW(
        "CONIN$", GENERIC_READ_WRITE, FILE_SHARE_READ_WRITE,
        None, OPEN_EXISTING, wintypes.DWORD(0), None,
    )

    # Point the Windows STD_INPUT_HANDLE at the real console
    kernel32.SetStdHandle(STD_INPUT_HANDLE, handle)

    # Fix fd 0 so msvcrt.get_osfhandle(0) returns the console handle
    try:
        os.close(sys.stdin.fileno())
    except OSError:
        pass
    new_fd = os.open("CONIN$", os.O_RDONLY)
    if new_fd != 0:
        os.dup2(new_fd, 0)
        os.close(new_fd)

    # Fix both sys.stdin and sys.__stdin__ — Textual reads from __stdin__
    new_stdin = os.fdopen(0, "r", closefd=False)
    sys.stdin = new_stdin  # type: ignore[assignment]
    sys.__stdin__ = new_stdin  # type: ignore[assignment]


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
        _reopen_stdin()
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
