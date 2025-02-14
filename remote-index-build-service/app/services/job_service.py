from typing import Optional
from models.job import Job, JobStatus, RequestParameters
from models.workflow import BuildWorkflow
from utils.hash import generate_job_id
from utils.memory import calculate_memory_requirements
from storage.base import RequestStore
from schemas.api import CreateJobRequest
from queue.base import PendingQueue

class JobService:
    def __init__(
            self,
            request_store: RequestStore,
            pending_queue: PendingQueue[BuildWorkflow],
            total_gpu_memory: float,
            total_cpu_memory: float
    ):
        self.request_store = request_store
        self.pending_queue = pending_queue
        self.total_gpu_memory = total_gpu_memory
        self.total_cpu_memory = total_cpu_memory


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

        # Check if pending queue is full
        if self.pending_queue.is_full():
            raise ValueError("Pending queue at capacity")

        gpu_mem, cpu_mem = calculate_memory_requirements(
            create_job_request.vector_parameters.dimension,
            create_job_request.vector_parameters.docs
        )

        if gpu_mem > self.total_gpu_memory or cpu_mem > self.total_cpu_memory:
            raise ValueError("Insufficient resources")

        workflow = BuildWorkflow(job_id, gpu_mem, cpu_mem, create_job_request)

        self.request_store.add(job_id, Job(job_id, JobStatus.RUNNING, request_parameters))

        self.pending_queue.add(workflow)

        return job_id

    def get_job(self, job_id: str) -> Optional[Job]:
        return self.request_store.get(job_id)

    def cancel_job(self, job_id: str) -> bool:
        return self.request_store.delete(job_id)
