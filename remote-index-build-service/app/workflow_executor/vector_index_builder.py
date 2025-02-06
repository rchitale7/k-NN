#  Copyright OpenSearch Contributors
#  SPDX-License-Identifier: Apache-2.0

from models.api import CreateIndexRequest
from index_builder.index_builder_factory import IndexBuilderFactory
from object_store.object_store_factory import ObjectStoreFactory
from metric.metric_factory import MetricFactory

import time

def build_index_and_upload_index(createIndexRequest: CreateIndexRequest, job_id: str):
    # initialize clients

    # initialize object store client, from docker settings
    object_store_client = ObjectStoreFactory.get_object_store_client()

    # initialize index builder client, from request params
    index_builder_client = IndexBuilderFactory.get_index_builder_client(createIndexRequest)

    # initialize metric client, from docker settings
    metric_client = MetricFactory.get_metric_client()

    # initialize vector store client, from docker settings
    start_time = time.time()
    vectors = object_store_client.get_vectors(createIndexRequest.object_path)
    end_time = time.time()

    # we can move this to inside the get_vectors function. This is just shown here as an example.
    metric_client.push_metric(
        {
            "vector_download_time": end_time - start_time,
            "job_id": job_id
        }
    )

    start_time = time.time()
    index = index_builder_client.build_index(vectors)
    end_time = time.time()

    # we can move this to inside the build_index function. This is just shown here as an example.
    metric_client.push_metric(
        {
            "total_index_build_time": end_time - start_time,
            "job_id": job_id
        }
    )

    start_time = time.time()
    object_store_client.upload_index(index)
    end_time = time.time()

    # we can move this to inside the upload_index function. This is just shown here as an example.
    metric_client.push_metric(
        {
            "vector_upload_time": end_time - start_time,
            "job_id": job_id
        }
    )
