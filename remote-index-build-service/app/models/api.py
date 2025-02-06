#  Copyright OpenSearch Contributors
#  SPDX-License-Identifier: Apache-2.0
from pydantic import BaseModel
from typing import Optional, Dict, Union

class Encoder(BaseModel):
    name: str
    parameters: Optional[Dict[str, Union[str, int]]] = None

class IndexParameters(BaseModel):
    ef_search: Optional[int] = None
    ef_construction: Optional[int] = None
    m: Optional[int] = None
    encoder: Optional[Encoder] = None

class VectorParameters(BaseModel):
    dimension: int
    docs: int

class CreateIndexRequest(BaseModel):
    repository_type: str
    container_name: str
    object_path: str
    tenant_id: str
    vector_parameters: VectorParameters
    index_parameters: Optional[IndexParameters] = None

class CreateIndexResponse(BaseModel):
    job_id: str

class GetStatusResponse(BaseModel):
    task_status: str
    graph_path: str