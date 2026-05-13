"""Count events in rolling time windows and raise when limits are exceeded."""

from collections import deque
from dataclasses import dataclass
from time import monotonic
from typing import Callable, Deque, Iterable, List, Optional, Tuple

__version__ = "0.1.0"
__author__ = "fx-kirin <fx.kirin@gmail.com>"
__all__ = ["EventCounter", "EventLimitError", "WatchWindow"]


@dataclass(frozen=True)
class WatchWindow:
    """A rolling window limit.

    ``seconds`` is the size of the rolling time window. ``limit`` is the
    number of events allowed inside that window.
    """

    seconds: float
    limit: int


class EventLimitError(RuntimeError):
    """Raised when an event causes a watched window to exceed its limit."""

    def __init__(self, window: WatchWindow, events_count: int) -> None:
        self.window = window
        self.events_count = events_count
        super().__init__(
            "Event limit exceeded: "
            f"{events_count} events in {window.seconds:g}s "
            f"(limit: {window.limit})"
        )


class EventCounter:
    """Count events across one or more rolling time windows.

    Args:
        windows: Optional iterable of ``(seconds, limit)`` pairs.
        clock: Optional monotonic clock function. This is mainly useful in
            tests; production code should normally use the default.
    """

    def __init__(
        self,
        windows: Optional[Iterable[Tuple[float, int]]] = None,
        *,
        clock: Callable[[], float] = monotonic,
    ) -> None:
        self._clock = clock
        self._windows: List[Tuple[WatchWindow, Deque[float]]] = []

        if windows is not None:
            for seconds, limit in windows:
                self.add_watch_window(seconds, limit)

    def add_watch_window(
        self,
        seconds: float,
        limit: Optional[int] = None,
        *,
        threshold: Optional[int] = None,
    ) -> None:
        """Add a rolling window.

        ``limit`` events are allowed during ``seconds``. The next event inside
        that same window raises ``EventLimitError``.
        """

        if limit is None:
            limit = threshold
        elif threshold is not None:
            raise ValueError("use either limit or threshold, not both")

        if limit is None:
            raise ValueError("limit must be specified")
        if seconds <= 0:
            raise ValueError("seconds must be greater than 0")
        if limit < 1:
            raise ValueError("limit must be greater than or equal to 1")

        self._windows.append((WatchWindow(seconds=seconds, limit=limit), deque()))

    def add_event(self, check_if_exceeded: bool = True) -> None:
        """Record an event and optionally raise if any window is exceeded."""

        now = self._clock()
        for window, events in self._windows:
            events.append(now)
            self._trim(window, events, now)

        if check_if_exceeded:
            self.raise_if_exceeded()

    def raise_if_exceeded(self) -> None:
        """Raise ``EventLimitError`` if any configured window is exceeded."""

        now = self._clock()
        for window, events in self._windows:
            self._trim(window, events, now)
            events_count = len(events)
            if events_count > window.limit:
                raise EventLimitError(window, events_count)

    def is_threshold_exceeded(self) -> None:
        """Backward-compatible alias for ``raise_if_exceeded``."""

        self.raise_if_exceeded()

    def exceeded_windows(self) -> List[Tuple[float, int, int]]:
        """Return ``(seconds, limit, events_count)`` for exceeded windows."""

        now = self._clock()
        exceeded = []
        for window, events in self._windows:
            self._trim(window, events, now)
            events_count = len(events)
            if events_count > window.limit:
                exceeded.append((window.seconds, window.limit, events_count))
        return exceeded

    def event_counts(self) -> List[Tuple[float, int, int]]:
        """Return ``(seconds, limit, events_count)`` for all watched windows."""

        now = self._clock()
        counts = []
        for window, events in self._windows:
            self._trim(window, events, now)
            counts.append((window.seconds, window.limit, len(events)))
        return counts

    @staticmethod
    def _trim(window: WatchWindow, events: Deque[float], now: float) -> None:
        threshold_time = now - window.seconds
        while events and events[0] <= threshold_time:
            events.popleft()
