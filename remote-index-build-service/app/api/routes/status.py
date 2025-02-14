#  Copyright OpenSearch Contributors
#  SPDX-License-Identifier: Apache-2.0
from fastapi import APIRouter, HTTPException, Request
from schemas.api import GetStatusResponse

router = APIRouter()

@router.get("/_status/{job_id}")
def get_status(job_id: str, request: Request) -> GetStatusResponse:

    job_service = request.app.state.job_service
    job = job_service.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return GetStatusResponse(task_status=job.status, knn_index_path=job.knn_index_path)