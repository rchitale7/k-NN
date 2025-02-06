from fastapi import FastAPI
from models.api import CreateIndexRequest, CreateIndexResponse, GetStatusResponse
from workflow_executor.indexing_service import IndexingService


app = FastAPI()
indexing_service = IndexingService()

@app.post("/_build")
def create_index(request: CreateIndexRequest) -> CreateIndexResponse:
    job_hashes = indexing_service.get_active_jobs
    request_hash = hash(request)
    if request_hash in job_hashes:
        return CreateIndexResponse(job_id=job_hashes[request_hash])
    else:
      job_id = indexing_service.enqueue_job(request)
      return CreateIndexResponse(job_id=job_id)


@app.get("/_status/{job_id}")
def get_status(job_id: str) -> GetStatusResponse:
    job = indexing_service.get_job(job_id)
    return GetStatusResponse(task_status="not implemented", graph_path="not_implemented")