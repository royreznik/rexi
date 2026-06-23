import dataclasses
import re
from typing import Any, Iterable, Match, Optional, cast

from colorama import Fore
from textual import on
from textual.app import App, ComposeResult, ReturnType
from textual.containers import Container, Horizontal, ScrollableContainer
from textual.screen import ModalScreen
from textual.widgets import Button, Header, Input, Label, Select, Static, TextArea

from .regex_help import REGEX_HELP

UNDERLINE = "\033[4m"
RESET_UNDERLINE = "\033[24m"


@dataclasses.dataclass
class GroupMatch:
    keys: list[int | str]
    value: str
    start: int
    end: int
    is_first: bool = False

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, GroupMatch):
            return False
        return (
            self.start == other.start
            and self.end == other.end
            and self.is_first == other.is_first
        )

    def __repr__(self) -> str:
        return f"Group \"{'|'.join(map(str, self.keys))}\": \"{self.value}\""


class Help(ModalScreen[None]):
    def compose(self) -> ComposeResult:
        with Container():
            yield Label("Help for regex:")
            with Horizontal():
                help_keys = "\n".join(REGEX_HELP.keys())
                help_values = "\n".join(REGEX_HELP.values())
                yield Static(help_keys, classes="helpKeys")
                yield Static(help_values, classes="helpValues")
            yield Button("Close", id="exitHelp", variant="success")

    @on(Button.Pressed, "#exitHelp")
    def back_to_app(self) -> None:
        self.app.pop_screen()


class ModalInput(ModalScreen[str]):

    def __init__(self, value: str, *args: Any, **kwargs: Any) -> None:
        self.input_value = value
        super().__init__(*args, **kwargs)

    def compose(self) -> ComposeResult:
        with Container(id="modal-container"):
            yield Label("Result content:")
            yield TextArea(
                text=self.input_value,
                id="inputModal",
                language=None,
            )
            with Horizontal():
                yield Button("Apply", id="applyOutput", variant="success")
                yield Button("Cancel", id="cancelOutput", variant="warning")

    @on(Button.Pressed, "#cancelOutput")
    def back_to_app(self) -> None:
        self.dismiss()

    @on(Button.Pressed, "#applyOutput")
    def save_and_back_to_app(self) -> None:
        self.input_value = str(self.query_one("#inputModal", TextArea).text)
        self.dismiss(result=self.input_value)


# noinspection SpellCheckingInspection
class RexiApp(App[ReturnType]):
    CSS_PATH = "rexi.tcss"

    AVAILABLE_MODES = ["finditer", "match"]

    def __init__(
        self,
        input_content: str,
        initial_mode: Optional[str] = None,
        initial_pattern: Optional[str] = None,
    ):
        initial_mode = initial_mode or RexiApp.AVAILABLE_MODES[0]
        if initial_mode not in RexiApp.AVAILABLE_MODES:
            raise ValueError(
                f"This regex mode isn't supported!"
                f"please choose from the following list: {RexiApp.AVAILABLE_MODES}"
            )

        super().__init__()
        self.input_content: str = input_content
        self.regex_modes: list[str] = RexiApp.AVAILABLE_MODES
        self.regex_current_mode: str = initial_mode
        self.pattern = initial_pattern

    def compose(self) -> ComposeResult:
        with Horizontal(id="inputs"):
            yield Input(
                value=self.pattern,
                id="pattern",
                placeholder="Enter regex pattern",
            )
            yield Select(
                zip(self.regex_modes, self.regex_modes),
                id="select",
                allow_blank=False,
                value=self.regex_current_mode,
            )
            yield Button("Modify content", id="modify")
            yield Button("Help", id="help")
        with ScrollableContainer(id="result"):
            with ScrollableContainer(id="output-container"):
                with Header():
                    yield Static("Result")
                yield Static(
                    self.input_content,
                    id="output",
                    markup=False,
                )
            with ScrollableContainer(id="groups-container"):
                with Header():
                    yield Static("Groups")
                yield Static(id="groups")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "help":
            self.push_screen(Help())
        elif event.button.id == "modify":
            self.push_screen(
                ModalInput(self.input_content),
                callback=self.update_input_content,
            )

    def update_input_content(self, result: str | None) -> None:
        if result is not None:
            self.input_content = result
        self.run_worker(
            self.update_regex(cast(Input, self.query_one("#pattern")).value),
            exclusive=True,
        )

    @on(Input.Changed, "#pattern")
    async def on_input_changed(self, message: Input.Changed) -> None:
        self.pattern = message.value
        self.run_worker(self.update_regex(message.value), exclusive=True)

    @on(Select.Changed, "#select")
    async def on_select_changed(self, message: Select.Changed) -> None:
        self.regex_current_mode = cast(str, message.value)
        self.run_worker(
            self.update_regex(cast(Input, self.query_one("#pattern")).value),
            exclusive=True,
        )

    async def update_regex(self, str_pattern: str) -> None:
        output_widget = self.query_one("#output", Static)
        groups_widget = self.query_one("#groups", Static)
        output_result = self.input_content
        groups_result = ""
        if str_pattern:
            try:
                pattern = re.compile(str_pattern, re.MULTILINE)
                matches: Optional[Iterable[Optional[Match[str]]]] = None
                if self.regex_current_mode == "match":
                    matches = [pattern.match(output_result)]
                elif self.regex_current_mode == "finditer":
                    matches = pattern.finditer(output_result)
                if matches:
                    groups = self.combine_matches_groups(matches)
                    groups_result = self.create_groups_output(groups)
                    output_result = self.create_highlighted_output(groups)
            except re.error as e:
                self.log(e)

        output_widget.update(output_result)
        groups_widget.update(groups_result)

    def create_highlighted_output(self, groups_matches: list["GroupMatch"]) -> str:
        output = ""
        starts = {group.start for group in groups_matches if not group.is_first}
        first_starts = {group.start for group in groups_matches if group.is_first}
        ends = {group.end for group in groups_matches if not group.is_first}
        first_ends = {group.end for group in groups_matches if group.is_first}
        input_length = len(self.input_content)
        for character in range(input_length):
            if character in first_starts and character not in first_ends:
                output += UNDERLINE
            if character in starts and character not in ends:
                output += Fore.RED
            if character in ends and character not in starts:
                output += Fore.RESET
            if character in first_ends and character not in first_starts:
                output += RESET_UNDERLINE
            output += self.input_content[character]

        if input_length in ends:
            output += Fore.RESET
        if input_length in first_ends:
            output += RESET_UNDERLINE

        return output

    @staticmethod
    def create_groups_output(groups_matches: list["GroupMatch"]) -> str:
        return "\n".join(
            [repr(group) for group in groups_matches if not group.is_first]
        )

    def combine_matches_groups(
        self, matches: Iterable[Optional[Match[str]]]
    ) -> list["GroupMatch"]:
        groups = [self._combine_groups(match) for match in matches if match]
        return [g for group in groups for g in group]

    @staticmethod
    def _combine_groups(match: Match[str]) -> list["GroupMatch"]:
        groups = [GroupMatch([0], match.group(0), *match.regs[0], is_first=True)]
        groups += [
            GroupMatch([index], group, start, end)
            for index, (group, (start, end)) in enumerate(
                zip(match.groups(), match.regs[1:]), start=1
            )
        ]

        for group_name, group in match.groupdict().items():
            start, end = match.span(group_name)
            group_match = GroupMatch([group_name], group, start, end)
            if group_match in groups:
                groups[groups.index(group_match)].keys.append(group_name)
        return groups
