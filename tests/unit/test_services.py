from __future__ import annotations

from dataclasses import dataclass, field

import pytest

from common.core.errors import SecurityError
from common.core.service import EmailWorkerService, FormIntakeService
from common.models.domain import MailMessage, ProviderType, QueuedEmailJob, SendResult
from common.providers.base import MailProvider
from common.repositories.memory import InMemorySubmissionRepository
from tests.fixtures.demo_config import demo_config


@dataclass
class CapturingQueue:
    jobs: list[QueuedEmailJob] = field(default_factory=list)

    def enqueue(self, job: QueuedEmailJob) -> None:
        self.jobs.append(job)


class PassingTurnstile:
    def verify(self, token: str, remote_ip: str | None, expected_hostname: str | None) -> bool:
        return True


class FailingTurnstile:
    def verify(self, token: str, remote_ip: str | None, expected_hostname: str | None) -> bool:
        return False


@dataclass
class CapturingProvider(MailProvider):
    sent: list[MailMessage] = field(default_factory=list)

    def send(self, message: MailMessage) -> SendResult:
        self.sent.append(message)
        return SendResult("primary-ses", ProviderType.SES, "provider-msg-1")


def test_form_intake_enqueues_valid_submission() -> None:
    configs = demo_config()
    submissions = InMemorySubmissionRepository()
    queue = CapturingQueue()
    service = FormIntakeService(configs, submissions, queue, PassingTurnstile())

    request_id = service.submit(
        site_id="demo-hotel",
        form_id="contact",
        payload={
            "name": "Jane",
            "email": "jane@example.test",
            "message": "Hello",
            "turnstile_token": "ok",
        },
        origin="https://demo.example",
        remote_ip="127.0.0.1",
    )

    assert request_id
    assert len(submissions.submissions) == 1
    assert len(queue.jobs) == 1


def test_form_intake_rejects_invalid_origin() -> None:
    service = FormIntakeService(
        demo_config(),
        InMemorySubmissionRepository(),
        CapturingQueue(),
        PassingTurnstile(),
    )

    with pytest.raises(SecurityError):
        service.submit(
            site_id="demo-hotel",
            form_id="contact",
            payload={
                "name": "Jane",
                "email": "jane@example.test",
                "message": "Hello",
                "turnstile_token": "ok",
            },
            origin="https://evil.example",
            remote_ip="127.0.0.1",
        )


def test_form_intake_rejects_failed_turnstile() -> None:
    service = FormIntakeService(
        demo_config(),
        InMemorySubmissionRepository(),
        CapturingQueue(),
        FailingTurnstile(),
    )

    with pytest.raises(SecurityError):
        service.submit(
            site_id="demo-hotel",
            form_id="contact",
            payload={
                "name": "Jane",
                "email": "jane@example.test",
                "message": "Hello",
                "turnstile_token": "bad",
            },
            origin="https://demo.example",
            remote_ip="127.0.0.1",
        )


def test_worker_sends_backend_configured_message() -> None:
    provider = CapturingProvider()
    submissions = InMemorySubmissionRepository()
    job = QueuedEmailJob(
        schema_version=1,
        message_id="msg-1",
        request_id="req-1",
        tenant_id="demo",
        site_id="demo-hotel",
        form_id="contact",
        submitted_at="2026-08-24T00:00:00+00:00",
        payload={"name": "Jane", "email": "jane@example.test", "message": "Hello"},
    )

    EmailWorkerService(demo_config(), submissions, provider).process(job)

    assert provider.sent[0].recipient.email == "owner@example.test"
    assert submissions.send_results[0][1].message_id == "provider-msg-1"
