#  Copyright OpenSearch Contributors
#  SPDX-License-Identifier: Apache-2.0

from abc import ABC, abstractmethod
from typing import Optional, Generic, TypeVar

T = TypeVar('T')

class PendingQueue(ABC, Generic[T]):
    @abstractmethod
    def add(self, item: T) -> bool:
        """Add item to queue"""
        pass

    @abstractmethod
    def get(self) -> Optional[T]:
        """Peek at the next item without removing it"""
        pass

    @abstractmethod
    def remove_first(self) -> Optional[T]:
        """Remove and return the first item in the queue"""
        pass

    @abstractmethod
    def size(self) -> int:
        """Get current queue size"""
        pass

    @abstractmethod
    def is_full(self) -> bool:
        """Check if queue is at capacity"""
        pass