from typing import cast

import pytest
from colorama import Fore
from textual.widgets import Static

from rexi.rexi import RexiApp, UNDERLINE, RESET_UNDERLINE


@pytest.mark.parametrize(
    ("start_mode", "pattern", "expected_output"),
    [
        [
            "match",
            ".*(aTe).*",
            f"{UNDERLINE}This iS! {Fore.RED}aTe{Fore.RESET} xt2 F0r T3sT!ng{RESET_UNDERLINE}",
        ],
        [
            "match",
            ".*(aTe.*)",
            f"{UNDERLINE}This iS! {Fore.RED}aTe xt2 F0r T3sT!ng{Fore.RESET}{RESET_UNDERLINE}",
        ],
        [
            "finditer",
            "(aTe)",
            f"This iS! {UNDERLINE}{Fore.RED}aTe{Fore.RESET}{RESET_UNDERLINE} xt2 F0r T3sT!ng",
        ],
    ],
)
async def test_input_box(start_mode: str, pattern: str, expected_output: str) -> None:
    app: RexiApp[int] = RexiApp("This iS! aTe xt2 F0r T3sT!ng", start_mode=start_mode)
    async with app.run_test() as pilot:
        await pilot.click("Input")
        await pilot.press(*list(pattern))
        result = str(cast(Static, app.query_one("#output")).renderable)
        assert result == expected_output


async def test_input_box_with_initial_pattern() -> None:
    app: RexiApp[int] = RexiApp(
        "This iS! aTe xt2 F0r T3sT!ng", initial_pattern="(This.*iS!)"
    )
    async with app.run_test():
        result = str(cast(Static, app.query_one("#output")).renderable)
        assert (
            result
            == f"{UNDERLINE}{Fore.RED}This iS!{Fore.RESET}{RESET_UNDERLINE} aTe xt2 F0r T3sT!ng"
        )


async def test_switch_modes() -> None:
    app: RexiApp[int] = RexiApp("This iS! aTe xt2 F0r T3sT!ng")
    async with app.run_test() as pilot:
        assert app.regex_current_mode == "finditer"
        await pilot.click("SelectCurrent")
        await pilot.click("SelectOverlay", offset=(2, 2))
        await pilot.wait_for_animation()
        assert app.regex_current_mode == "match"
