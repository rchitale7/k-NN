#  Copyright OpenSearch Contributors
#  SPDX-License-Identifier: Apache-2.0
from pydantic import BaseModel
from models.job import Job

class BuildWorkflow(BaseModel):
    job: Job
    vector_dimensions: int
    num_vectors: int
    gpu_memory_required: float
    cpu_memory_required: float
