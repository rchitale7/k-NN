#  Copyright OpenSearch Contributors
#  SPDX-License-Identifier: Apache-2.0
from fastapi import APIRouter
from services.job_service import job_service
from schemas.api import CreateJobRequest, CreateJobResponse

router = APIRouter()

@router.post("/_build")
def create_job(request: CreateJobRequest) -> CreateJobResponse:
    job_id = job_service.create_job(request)
    return CreateJobResponse(job_id=job_id)