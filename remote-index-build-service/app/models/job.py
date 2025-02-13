#  Copyright OpenSearch Contributors
#  SPDX-License-Identifier: Apache-2.0
from enum import Enum
from pydantic import BaseModel

class RequestParameters(BaseModel):
    object_path: str
    tenant_id: str

    def __str__(self):
        return f"{self.object_path}-{self.tenant_id}"

    def __eq__(self, other):
        if not isinstance(other, RequestParameters):
            return False
        return str(self) == str(other)

class JobStatus(str, Enum):
    RUNNING = "RUNNING_INDEX_BUILD"
    FAILED = "FAILED_INDEX_BUILD"
    COMPLETED = "COMPLETED_INDEX_BUILD"

class Job(BaseModel):
    id: str
    status: JobStatus
    request_parameters: RequestParameters
    knn_index_path: str = ""

    def compare_request_parameters(self, other: RequestParameters) -> bool:
        return self.request_parameters == other