#  Copyright OpenSearch Contributors
#  SPDX-License-Identifier: Apache-2.0
from pydantic import BaseModel

class Job(BaseModel):
    job_id: str
    task_status: str