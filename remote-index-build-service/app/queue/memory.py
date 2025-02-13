#  Copyright OpenSearch Contributors
#  SPDX-License-Identifier: Apache-2.0

from typing import Optional, Generic, TypeVar
from collections import deque
import threading
from queue.base import PendingQueue

T = TypeVar('T')

class InMemoryPendingQueue(PendingQueue[T]):
    def __init__(self, max_size: int):
        self._queue = deque()
        self._max_size = max_size
        self._lock = threading.Lock()

    def add(self, item: T) -> bool:
        with self._lock:
            if len(self._queue) >= self._max_size:
                return False
            self._queue.append(item)
            return True

    def get(self) -> Optional[T]:
        """Peek at the next item without removing it"""
        with self._lock:
            return self._queue[0] if self._queue else None

    def remove_first(self) -> Optional[T]:
        """Remove and return the first item in the queue"""
        with self._lock:
            return self._queue.popleft() if self._queue else None

    def size(self) -> int:
        with self._lock:
            return len(self._queue)

    def is_full(self) -> bool:
        with self._lock:
            return len(self._queue) >= self._max_size