"""Line-coverage suite for the assigned library fines application."""

import pytest

from library_fines import can_borrow, late_fine, renewal_status


def test_late_fine_validation():
    with pytest.raises(ValueError, match="unknown member"):
        late_fine("unknown", 0, False)
    with pytest.raises(ValueError, match="invalid days"):
        late_fine("student", -1, False)


def test_late_fine_paths():
    assert late_fine("faculty", 30, False) == 0
    assert late_fine("student", 15, False) == 2
    assert late_fine("guest", 55, True) == 350


def test_borrowing_paths():
    assert can_borrow(0, 101, "student") is False
    assert can_borrow(9, 0, "faculty") is True
    assert can_borrow(2, 0, "student") is True


def test_renewal_paths():
    assert renewal_status(0, True, 1) == "denied"
    assert renewal_status(2, False, 1) == "limit reached"
    assert renewal_status(0, False, -1) == "overdue"
    assert renewal_status(0, False, 0) == "renewed"
