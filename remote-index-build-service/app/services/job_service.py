from typing import Optional
from models.job import Job, JobStatus, RequestParameters
from models.workflow import BuildWorkflow
from utils.hash import generate_job_id
from storage.base import RequestStore
from schemas.api import CreateJobRequest
from queue.base import PendingQueue

class JobService:
    def __init__(
            self,
            request_store: RequestStore,
            pending_queue: PendingQueue[BuildWorkflow]
    ):
        self.request_store = request_store
        self.pending_queue = pending_queue


    def create_job(self, create_job_request: CreateJobRequest) -> str:

        request_parameters = RequestParameters(
            create_job_request.object_path,
            create_job_request.tenant_id
        )

        job_id = generate_job_id(request_parameters)

        # Check if job already exists
        existing_job = self.request_store.get(job_id)
        if existing_job:
            if existing_job.compare_request_parameters(request_parameters):
                return job_id
            raise ValueError("Hash collision detected")

        workflow = BuildWorkflow(create_job_request)

        # Add to pending queue
        if not self.pending_queue.add(workflow):
            # If queue is full, delete job and raise error
            self.request_store.delete(job_id)
            raise ValueError("Pending queue at capacity")

        return job_id

    def get_job(self, job_id: str) -> Optional[Job]:
        return self.request_store.get(job_id)

    def cancel_job(self, job_id: str) -> bool:
        return self.request_store.delete(job_id)
