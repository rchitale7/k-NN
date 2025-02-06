from models.api import CreateIndexRequest
from models.job import job

class IndexingService:

    def __init__(self):
        pass

    def get_active_jobs(self, createIndexRequest: CreateIndexRequest):
        pass

    def enqueue_job(self, createIndexRequest: CreateIndexRequest):
        pass

    def get_job(self, job_id: str):
        return job.Job(job_id=job_id, status="NOT IMPLEMENTED!", graph_path="NOT IMPLEMENTED!")