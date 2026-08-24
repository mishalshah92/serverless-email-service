"""Configuration and persistence repositories."""

from email_service.repositories.memory import InMemoryConfigRepository, InMemorySubmissionRepository

__all__ = ["InMemoryConfigRepository", "InMemorySubmissionRepository"]
