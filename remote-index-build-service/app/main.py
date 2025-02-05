from fastapi import FastAPI
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

class CreateIndexRequest(BaseModel):
    repository_type: str
    container_name: str
    object_path: str
    tenant_id: str
    index_parameters: Optional[IndexParameters] = None


app = FastAPI()

@app.post("/_build")
def create_index(request: CreateIndexRequest):
    return {
        "job_id": "Not implemented yet!"
    }


@app.get("/_status/{build_id}")
def get_status(build_id: str):
    return {
        "task_status": "Not implemented yet!",
        "graph_path": "Not implemented yet!"
    }