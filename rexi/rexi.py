import dataclasses
import os
import re
import sys
from typing import cast, Match, Iterable, Optional

from colorama import Fore
from textual import on
from textual.app import App, ComposeResult, ReturnType
from textual.containers import ScrollableContainer, Horizontal
from textual.widgets import Input, Static, Header, Select


@dataclasses.dataclass
class GroupMatch:
    keys: list[int | str]
    value: str
    start: int
    end: int

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, GroupMatch):
            return False
        return self.start == other.start and self.end == other.end

    def __repr__(self) -> str:
        return f"Group \"{'|'.join(map(str, self.keys))}\": \"{self.value}\""


# noinspection SpellCheckingInspection
class RexiApp(App[ReturnType]):
    CSS_PATH = "rexi.tcss"

    def __init__(self, input_content: str):
        super().__init__()
        self.input_content: str = input_content
        self.regex_modes: list[str] = ["match", "finditer"]
        self.regex_current_mode: str = self.regex_modes[0]

    def compose(self) -> ComposeResult:
        with Horizontal(id="inputs"):
            yield Input(placeholder="Enter regex pattern")
            yield Select(
                zip(self.regex_modes, self.regex_modes), id="select", allow_blank=False
            )

        with ScrollableContainer(id="result"):
            with ScrollableContainer(id="output-container"):
                with Header():
                    yield Static("Result")
                yield Static(self.input_content, id="output", markup=False)
            with ScrollableContainer(id="groups-container"):
                with Header():
                    yield Static("Groups")
                yield Static(id="groups")

    @on(Input.Changed)
    async def on_input_changed(self, message: Input.Changed) -> None:
        self.run_worker(self.update_regex(message.value), exclusive=True)

    @on(Select.Changed)
    async def on_select_changed(self, message: Select.Changed) -> None:
        self.regex_current_mode = cast(str, message.value)
        self.run_worker(
            self.update_regex(cast(Input, self.query_one("Input")).value),
            exclusive=True,
        )

    async def update_regex(self, str_pattern: str) -> None:
        output_widget = self.query_one("#output", Static)
        groups_widget = self.query_one("#groups", Static)
        output_result = ""
        groups_result = ""
        if str_pattern:
            try:
                pattern = re.compile(str_pattern, re.MULTILINE)
                matches: Optional[Iterable[Optional[Match[str]]]] = None
                if self.regex_current_mode == "match":
                    matches = [pattern.match(self.input_content)]
                elif self.regex_current_mode == "finditer":
                    matches = pattern.finditer(self.input_content)
                if matches:
                    groups = self.combine_matches_groups(matches)
                    groups_result = self.create_groups_output(groups)
                    output_result = self.create_highlighted_output(groups)
            except re.error as e:
                self.log(e)

        output_widget.update(output_result or self.input_content)
        groups_widget.update(groups_result)

    def create_highlighted_output(self, groups_matches: list["GroupMatch"]) -> str:
        output = ""
        starts = {group.start for group in groups_matches}
        ends = {group.end for group in groups_matches}
        for character in range(len(self.input_content)):
            if character in starts:
                output += Fore.RED
            output += self.input_content[character]
            if character in ends:
                output += Fore.RESET
        return output

    @staticmethod
    def create_groups_output(groups_matches: list["GroupMatch"]) -> str:
        return "\n".join(map(repr, groups_matches))

    def combine_matches_groups(self, matches: Iterable[Optional[Match[str]]]) -> list["GroupMatch"]:
        groups = [self._combine_groups(match) for match in matches if match]
        return [g for group in groups for g in group]

    @staticmethod
    def _combine_groups(match: Match[str]) -> list["GroupMatch"]:
        groups = [
            GroupMatch([index], group, start, end)
            for index, (group, (start, end)) in enumerate(
                zip(match.groups(), match.regs)
            )
        ]
        for group_name, group in match.groupdict().items():
            start, end = match.span(group_name)
            group_match = GroupMatch([group_name], group, start, end)
            if group_match in groups:
                groups[groups.index(group_match)].keys.append(group_name)
        return groups


def main() -> None:
    stdin = sys.stdin.read()
    os.close(sys.stdin.fileno())
    sys.stdin = open("/dev/tty", "rb")  # type: ignore[assignment]

    app: RexiApp[int] = RexiApp(stdin)
    app.run()
