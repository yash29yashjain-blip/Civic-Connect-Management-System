
from services.complaint_service import VALID_STATUSES


def test_valid_complaint_statuses():
    assert "Submitted" in VALID_STATUSES
    assert "Assigned" in VALID_STATUSES
    assert "In Progress" in VALID_STATUSES
    assert "Resolved" in VALID_STATUSES
    assert "Rejected" in VALID_STATUSES


def test_unknown_status_is_not_valid():
    assert "Closed Forever" not in VALID_STATUSES


def test_priority_options():
    valid_priorities = {"Low", "Medium", "High", "Urgent"}
    assert "Urgent" in valid_priorities
    assert "Normalised" not in valid_priorities
