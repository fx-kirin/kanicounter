"""kanicounter - """

__version__ = '0.1.0'
__author__ = 'fx-kirin <fx.kirin@gmail.com>'
__all__: list = []


import time
from collections import deque

class EventLimitError(RuntimeError):
    def __init__(self, message):
        super().__init__(message)


class EventCounter:
    def __init__(self):
        # ウィンドウ設定: list of dict { 'seconds': int, 'threshold': int, 'events': deque }
        self._windows = []

    def add_watch_window(self, seconds, threshold):
        # 監視ウィンドウを追加
        self._windows.append({
            'seconds': seconds,
            'threshold': threshold,
            'events': deque()
        })

    def add_event(self, check_if_exceeded=True):
        now = time.time()
        for window in self._windows:
            window['events'].append(now)
            self._trim(window)
        if check_if_exceeded:
            self.is_threshold_exceeded()

    def _trim(self, window):
        threshold_time = time.time() - window['seconds']
        dq = window['events']
        while dq and dq[0] < threshold_time:
            dq.popleft()

    def is_threshold_exceeded(self):
        for w in self._windows:
            if len(w['events']) >= w['threshold']:
                seconds = w['seconds']
                threshold = w['threshold']
                events_len = len(w['events'])
                raise EventLimitError(f"EventLimit was exceeded. {seconds=} {threshold=} {events_len=}")

    def exceeded_windows(self):
        # 超えているウィンドウのリストを返す
        return [
            (w['seconds'], w['threshold'], len(w['events']))
            for w in self._windows
            if len(w['events']) >= w['threshold']
        ]
