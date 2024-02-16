import re

import pytest

from rexi.rexi import GroupMatch, RexiApp


@pytest.mark.parametrize(
    ("group_one", "group_two", "expected_equals"),
    [
        [GroupMatch([1], "name", 1, 2), GroupMatch([2], "name2", 1, 2), True],
        [GroupMatch([1], "name", 1, 2), GroupMatch([2], "name2", 1, 2), True],
        [GroupMatch([1], "name", 1, 2), GroupMatch([1], "name", 1, 3), False],
        [GroupMatch([1], "name", 1, 3), GroupMatch([1], "name", 2, 3), False],
        [GroupMatch([1], "name", 1, 3), object(), False],
    ],
)
def test_group_match_equals(
    group_one: GroupMatch, group_two: GroupMatch, expected_equals: bool
) -> None:
    assert (group_one == group_two) == expected_equals


@pytest.mark.parametrize(
    ("pattern", "content", "expected_groups"),
    [
        [
            ".*(aTe).*",
            "This iS! aTe xt2 F0r T3sT!ng",
            [
                GroupMatch([0], "This iS! aTe xt2 F0r T3sT!ng", 0, 28, True),
                GroupMatch([1], "aTe", 9, 12),
            ],
        ],
        [
            ".*(?P<name>aTe).*",
            "This iS! aTe xt2 F0r T3sT!ng",
            [
                GroupMatch([0], "This iS! aTe xt2 F0r T3sT!ng", 0, 28, True),
                GroupMatch([1, "name"], "aTe", 9, 12),
            ],
        ],
    ],
)
def test_combine_groups(
    pattern: str, content: str, expected_groups: list[GroupMatch]
) -> None:
    matches = re.match(pattern, content)
    assert matches  # sanity
    result = RexiApp._combine_groups(matches)
    assert result == expected_groups, result[0].end
