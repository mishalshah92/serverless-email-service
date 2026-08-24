"""Configuration and persistence repositories."""

from common.repositories.memory import InMemoryConfigRepository, InMemorySubmissionRepository

__all__ = ["InMemoryConfigRepository", "InMemorySubmissionRepository"]
