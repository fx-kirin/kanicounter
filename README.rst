kanicounter
===========

``kanicounter`` is a small Python library for counting events in rolling time
windows. It raises an exception when an event exceeds the allowed count.

Usage
-----

.. code-block:: python

    from kanicounter import EventCounter, EventLimitError

    counter = EventCounter()
    counter.add_watch_window(seconds=60, limit=10)

    try:
        counter.add_event()
    except EventLimitError as exc:
        print(exc)

``limit`` is the number of events allowed inside the window. For example,
``seconds=60, limit=10`` allows 10 events in the last 60 seconds and raises
``EventLimitError`` on the 11th event.

Installation
------------

.. code-block:: console

    pip install kanicounter

Requirements
------------

Python 3.8 or newer. There are no runtime dependencies.

Licence
-------

MIT

Authors
-------

``kanicounter`` was written by `fx-kirin <mailto:fx.kirin@gmail.com>`_.
