#  Copyright OpenSearch Contributors
#  SPDX-License-Identifier: Apache-2.0
class BuildServiceError(Exception):
    """Base exception for build service errors"""
    pass

class BuildError(BuildServiceError):
    """Raised when there's an error during index building"""
    pass

class ObjectStoreError(BuildServiceError):
    """Raised when there's an error with object store operations"""
    pass

class ResourceError(BuildServiceError):
    """Raised when there's an error managing resources"""
    pass

class QueueException(BuildServiceError):
    """Raised when there's an exception processing request from queue"""
    pass