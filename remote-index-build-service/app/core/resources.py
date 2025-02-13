#  Copyright OpenSearch Contributors
#  SPDX-License-Identifier: Apache-2.0

import threading
from typing import Optional

class ResourceManager:
    def __init__(self, total_gpu_memory: float, total_cpu_memory: float):
        self._total_gpu_memory = total_gpu_memory
        self._total_cpu_memory = total_cpu_memory
        self._available_gpu_memory = total_gpu_memory
        self._available_cpu_memory = total_cpu_memory
        self._lock = threading.Lock()

    def can_allocate(self, gpu_memory: float, cpu_memory: float) -> bool:
        with self._lock:
            return (self._available_gpu_memory >= gpu_memory and
                    self._available_cpu_memory >= cpu_memory)

    def allocate(self, gpu_memory: float, cpu_memory: float) -> bool:
        with self._lock:
            if not self.can_allocate(gpu_memory, cpu_memory):
                return False
            self._available_gpu_memory -= gpu_memory
            self._available_cpu_memory -= cpu_memory
            return True

    def release(self, gpu_memory: float, cpu_memory: float) -> None:
        with self._lock:
            self._available_gpu_memory += gpu_memory
            self._available_cpu_memory += cpu_memory