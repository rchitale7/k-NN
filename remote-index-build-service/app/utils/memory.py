#  Copyright OpenSearch Contributors
#  SPDX-License-Identifier: Apache-2.0

def calculate_memory_requirements(
        vector_dimensions: int,
        num_vectors: int
) -> tuple[float, float]:
    """
    Calculate GPU and CPU memory requirements for a vector workload.
    Returns (gpu_memory_gb, cpu_memory_gb)
    """
    # Vector memory (same for both GPU and CPU)
    vector_memory = vector_dimensions * num_vectors * 4  # 4 bytes per float32

    # GPU memory (includes extra space for index construction)
    gpu_memory = (vector_memory * 1.5) / (1024 ** 3)  # Convert to GB

    # CPU memory (includes space for both vectors and final index)
    cpu_memory = (vector_memory * 2) / (1024 ** 3)  # Convert to GB

    return gpu_memory, cpu_memory