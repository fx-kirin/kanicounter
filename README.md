# kanicounter

`kanicounter` is a small Python library for counting events in rolling time
windows. It raises an exception when an event exceeds the allowed count.

## Usage

```python
from kanicounter import EventCounter, EventLimitError

counter = EventCounter()
counter.add_watch_window(seconds=60, limit=10)

try:
    counter.add_event()
except EventLimitError as exc:
    print(exc)
```

`limit` is the number of events allowed inside the window. For example,
`seconds=60, limit=10` allows 10 events in the last 60 seconds and raises
`EventLimitError` on the 11th event.

You can watch multiple windows at the same time:

```python
counter = EventCounter([
    (1, 5),      # allow 5 events per second
    (60, 100),  # allow 100 events per minute
])

counter.add_event()
```

If you want to inspect limits without raising immediately, disable the check
when recording an event:

```python
counter.add_event(check_if_exceeded=False)

for seconds, limit, events_count in counter.exceeded_windows():
    print(seconds, limit, events_count)
```

## Installation

```console
pip install kanicounter
```

For local development:

```console
python -m pip install -e .
python -m pip install pytest
python -m pytest
```

## Requirements

Python 3.8 or newer. There are no runtime dependencies.

## Compatibility

The library uses a monotonic clock by default, so it is suitable for rolling
runtime limits such as rate checks and burst detection.

## Licence

MIT

## Authors

kanicounter was written by [fx-kirin](mailto:fx.kirin@gmail.com).
