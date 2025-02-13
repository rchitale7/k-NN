#  Copyright OpenSearch Contributors
#  SPDX-License-Identifier: Apache-2.0

from enum import Enum
from storage.base import RequestStore
from storage.memory import InMemoryRequestStore
from core.config import Settings

class RequestStoreType(str, Enum):
    MEMORY = "memory"

class RequestStoreFactory:
    @staticmethod
    def create(store_type: RequestStoreType, settings: Settings) -> RequestStore:
        if store_type == RequestStoreType.MEMORY:
            return InMemoryRequestStore(settings)
        else:
            raise ValueError(f"Unsupported request store type: {store_type}")