#  Copyright OpenSearch Contributors
#  SPDX-License-Identifier: Apache-2.0

import threading
import time
import logging
from typing import Callable, Optional
from queue.base import PendingQueue
from models.workflow import BuildWorkflow
from core.resources import ResourceManager
from storage.base import RequestStore
from executors.workflow_executor import WorkflowExecutor
from models.job import JobStatus

logger = logging.getLogger(__name__)

class QueueProcessor:
    def __init__(
        self,
        pending_queue: PendingQueue[BuildWorkflow],
        request_store: RequestStore,
        resource_manager: ResourceManager,
        workflow_executor: WorkflowExecutor,
        check_interval: int = 5
    ):
        self.pending_queue = pending_queue
        self.request_store = request_store
        self.resource_manager = resource_manager
        self.workflow_executor = workflow_executor
        self.check_interval = check_interval
        self._stop_event = threading.Event()
        self._processor_thread: Optional[threading.Thread] = None

    def start(self):
        """Start the queue processor"""
        if self._processor_thread is not None:
            return

        self._stop_event.clear()
        self._processor_thread = threading.Thread(
            target=self._process_queue,
            daemon=True
        )
        self._processor_thread.start()

    def stop(self):
        """Stop the queue processor"""
        self._stop_event.set()
        if self._processor_thread is not None:
            self._processor_thread.join()
            self._processor_thread = None

    def _process_queue(self):
        """Main processing loop"""
        while not self._stop_event.is_set():
            try:
                self._process_next_workflow()
            except Exception as e:
                logger.error(f"Error processing workflow: {e}", exc_info=True)

            # Sleep before next check
            self._stop_event.wait(self.check_interval)

    def _process_next_workflow(self):
        """Process the next workflow in the queue"""
        workflow = self.pending_queue.get()
        if not workflow:
            return

        # Check if job still exists (hasn't been cancelled)
        if not self.request_store.get(workflow.job.id):
            logger.info(f"Job {workflow.job.id} was cancelled, skipping processing")
            self.pending_queue.remove_first()  # Remove cancelled job
            return

        # Check resource availability
        if not self.resource_manager.can_allocate(
                workflow.gpu_memory_required,
                workflow.cpu_memory_required
        ):
            return

        # Allocate resources
        self.resource_manager.allocate(
            workflow.gpu_memory_required,
            workflow.cpu_memory_required
        )

        # Submit to workflow executor
        if not self.workflow_executor.submit_workflow(workflow):
            # Only remove from queue if successfully submitted
            self.pending_queue.remove_first()
        else:
            self.resource_manager.release(
                workflow.gpu_memory_required,
                workflow.cpu_memory_required
            )