import pytest
from niche_trend_tracker import NicheTrendTracker

def test_init_default_mode():
    tracker = NicheTrendTracker()
    assert tracker.mode == "mock"

def test_init_mock_mode():
    tracker = NicheTrendTracker(mode="mock")
    assert tracker.mode == "mock"

def test_init_live_mode():
    tracker = NicheTrendTracker(mode="live")
    assert tracker.mode == "live"
    def test_init_sets_mode_to_mock_by_default():
        tracker = NicheTrendTracker()
        assert tracker.mode == "mock"

    def test_init_sets_mode_to_mock_explicit():
        tracker = NicheTrendTracker(mode="mock")
        assert tracker.mode == "mock"

    def test_init_sets_mode_to_live():
        tracker = NicheTrendTracker(mode="live")
        assert tracker.mode == "live"

    def test_init_accepts_arbitrary_mode_string():
        tracker = NicheTrendTracker(mode="custom")
        assert tracker.mode == "custom"
