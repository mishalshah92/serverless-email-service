from __future__ import annotations

from uuid import uuid4

from common.core.errors import DisabledError, SecurityError
from common.core.ports import (
    ConfigRepository,
    QueueProducer,
    SubmissionRepository,
    TurnstileVerifier,
)
from common.core.validation import validate_form_payload
from common.models.domain import QueuedEmailJob, Submission
from common.providers.base import MailProvider
from common.security.request import validate_origin
from common.templates.renderer import render_mail_message


class FormIntakeService:
    def __init__(
        self,
        configs: ConfigRepository,
        submissions: SubmissionRepository,
        queue: QueueProducer,
        turnstile: TurnstileVerifier,
    ) -> None:
        self._configs = configs
        self._submissions = submissions
        self._queue = queue
        self._turnstile = turnstile

    def submit(
        self,
        *,
        site_id: str,
        form_id: str,
        payload: dict[str, object],
        origin: str | None,
        remote_ip: str | None,
        expected_hostname: str | None = None,
    ) -> str:
        form = self._configs.get_form(site_id, form_id)
        if not form.enabled:
            raise DisabledError("form is disabled")
        validate_origin(form, origin)
        if form.turnstile_required:
            token = str(payload.get("turnstile_token", ""))
            if not token or not self._turnstile.verify(token, remote_ip, expected_hostname):
                raise SecurityError("turnstile verification failed")
        normalized = validate_form_payload(form, payload)
        submission = Submission(
            request_id=str(uuid4()),
            tenant_id=form.tenant_id,
            site_id=form.site_id,
            form_id=form.form_id,
            payload=normalized,
        )
        job = QueuedEmailJob.from_submission(submission)
        self._submissions.save_submission(submission)
        self._queue.enqueue(job)
        return submission.request_id


class EmailWorkerService:
    def __init__(
        self,
        configs: ConfigRepository,
        submissions: SubmissionRepository,
        provider: MailProvider,
    ) -> None:
        self._configs = configs
        self._submissions = submissions
        self._provider = provider

    def process(self, job: QueuedEmailJob) -> None:
        form = self._configs.get_form(job.site_id, job.form_id)
        if not form.enabled:
            raise DisabledError("form is disabled")
        template = self._configs.get_template(job.tenant_id, form.template_id)
        message = render_mail_message(form, template, job.payload, request_id=job.request_id)
        try:
            result = self._provider.send(message)
        except Exception as exc:
            self._submissions.record_failure(job, str(exc))
            raise
        self._submissions.record_send_result(job, result)
