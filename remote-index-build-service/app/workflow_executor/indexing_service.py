from models.api import CreateIndexRequest
from models.job import Job

class IndexingService:

    def __init__(self):
        pass

    def get_active_jobs(self, createIndexRequest: CreateIndexRequest):
        pass

    def enqueue_job(self, createIndexRequest: CreateIndexRequest):
        pass

    def get_job(self, job_id: str):
        pass