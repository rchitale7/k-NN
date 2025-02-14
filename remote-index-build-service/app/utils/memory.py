#  Copyright OpenSearch Contributors
#  SPDX-License-Identifier: Apache-2.0

def calculate_memory_requirements(
        vector_dimensions: int,
        num_vectors: int
) -> tuple[float, float]:
    """
        Calculate GPU and CPU memory requirements for a vector workload.

        This function estimates the memory needed for processing vector operations,
        taking into account the workload size and complexity.

        Returns:
        tuple[float, float]: A tuple containing:
            - gpu_memory_gb (float): Required GPU memory in gigabytes
            - cpu_memory_gb (float): Required CPU memory in gigabytes
    """
    # Vector memory (same for both GPU and CPU)
    vector_memory = vector_dimensions * num_vectors * 4  # 4 bytes per float32

    m = 16

    # use formula to calculate memory in GB
    gpu_memory = ((vector_dimensions*4 + m*16) * 1.1 * num_vectors / (2 ** 30)) * 1.5

    cpu_memory = (vector_dimensions*4 + m*16) * 1.1 * num_vectors / (2 ** 30)

    return (gpu_memory + vector_memory), (cpu_memory + vector_memory)