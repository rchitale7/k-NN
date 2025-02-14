#  Copyright OpenSearch Contributors
#  SPDX-License-Identifier: Apache-2.0
from fastapi import APIRouter, Request
from schemas.api import CreateJobRequest, CreateJobResponse

router = APIRouter()

@router.post("/_build")
def create_job(create_job_request: CreateJobRequest, request: Request) -> CreateJobResponse:
    job_service = request.app.state.job_service
    job_id = job_service.create_job(create_job_request)
    return CreateJobResponse(job_id=job_id)