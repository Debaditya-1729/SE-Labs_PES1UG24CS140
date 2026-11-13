"""Decision branches and boundaries for the library fines application."""

import pytest

from library_fines import can_borrow, late_fine, renewal_status


@pytest.mark.parametrize("member", ["", "Student", "unknown"])
def test_unknown_members_are_rejected(member):
    with pytest.raises(ValueError, match="unknown member"):
        late_fine(member, 0, False)


def test_negative_days_are_rejected():
    with pytest.raises(ValueError, match="invalid days"):
        late_fine("student", -1, False)


@pytest.mark.parametrize(
    "member, days, damaged, expected",
    [
        ("student", 0, False, 0),
        ("student", 14, False, 0),
        ("student", 15, False, 2),
        ("faculty", 30, False, 0),
        ("faculty", 31, False, 1),
        ("guest", 14, False, 0),
        ("guest", 15, False, 5),
        ("student", 114, False, 200),  # exactly the cap
        ("student", 115, False, 200),  # above the cap
        ("student", 14, True, 150),
        ("student", 115, True, 350),  # damage is added after the cap
    ],
)
def test_fine_boundaries(member, days, damaged, expected):
    assert late_fine(member, days, damaged) == expected


@pytest.mark.parametrize(
    "held, fine, member, expected",
    [
        (0, 101, "faculty", False),
        (9, 100, "faculty", True),
        (10, 100, "faculty", False),
        (2, 100, "student", True),
        (3, 100, "student", False),
        (2, 0, "guest", True),
        (3, 0, "guest", False),
    ],
)
def test_borrowing_boundaries(held, fine, member, expected):
    assert can_borrow(held, fine, member) is expected


def test_reservation_takes_priority_over_limit_and_overdue():
    assert renewal_status(2, True, -1) == "denied"


def test_renewal_limit_takes_priority_over_overdue():
    assert renewal_status(2, False, -1) == "limit reached"


@pytest.mark.parametrize(
    "renewed, days_left, expected",
    [(1, -1, "overdue"), (1, 0, "renewed"), (1, 1, "renewed"),
     (2, 1, "limit reached")],
)
def test_renewal_boundaries(renewed, days_left, expected):
    assert renewal_status(renewed, False, days_left) == expected
