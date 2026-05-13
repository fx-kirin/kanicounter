import pytest

from kanicounter import EventCounter, EventLimitError, WatchWindow


class FakeClock:
    def __init__(self, initial=0.0):
        self.now = initial

    def __call__(self):
        return self.now

    def advance(self, seconds):
        self.now += seconds


def test_allows_events_up_to_limit():
    clock = FakeClock()
    counter = EventCounter([(10, 3)], clock=clock)

    counter.add_event()
    counter.add_event()
    counter.add_event()

    assert counter.event_counts() == [(10, 3, 3)]
    assert counter.exceeded_windows() == []


def test_raises_when_event_exceeds_limit():
    clock = FakeClock()
    counter = EventCounter([(10, 2)], clock=clock)

    counter.add_event()
    counter.add_event()

    with pytest.raises(EventLimitError) as exc_info:
        counter.add_event()

    error = exc_info.value
    assert error.window == WatchWindow(seconds=10, limit=2)
    assert error.events_count == 3
    assert "3 events in 10s" in str(error)


def test_expires_events_outside_rolling_window():
    clock = FakeClock()
    counter = EventCounter([(10, 2)], clock=clock)

    counter.add_event()
    clock.advance(10)
    counter.add_event()
    counter.add_event()

    assert counter.event_counts() == [(10, 2, 2)]


def test_can_report_exceeded_windows_without_raising():
    clock = FakeClock()
    counter = EventCounter([(10, 1), (60, 3)], clock=clock)

    counter.add_event(check_if_exceeded=False)
    counter.add_event(check_if_exceeded=False)

    assert counter.exceeded_windows() == [(10, 1, 2)]


def test_keeps_threshold_keyword_for_compatibility():
    counter = EventCounter()

    counter.add_watch_window(seconds=10, threshold=2)

    counter.add_event(False)
    assert counter.event_counts() == [(10, 2, 1)]


def test_multiple_windows_raise_on_first_exceeded_window():
    clock = FakeClock()
    counter = EventCounter([(1, 10), (60, 2)], clock=clock)

    counter.add_event()
    counter.add_event()

    with pytest.raises(EventLimitError) as exc_info:
        counter.add_event()

    assert exc_info.value.window == WatchWindow(seconds=60, limit=2)


@pytest.mark.parametrize(
    ("seconds", "limit", "message"),
    [
        (0, 1, "seconds must be greater than 0"),
        (-1, 1, "seconds must be greater than 0"),
        (1, 0, "limit must be greater than or equal to 1"),
        (1, None, "limit must be specified"),
    ],
)
def test_validates_watch_window(seconds, limit, message):
    counter = EventCounter()

    with pytest.raises(ValueError, match=message):
        counter.add_watch_window(seconds, limit)
