from __future__ import annotations

from typing import Any

from email_service.core.errors import ProviderError
from email_service.models.domain import MailMessage, ProviderType, SendResult


class SesMailProvider:
    def __init__(
        self,
        provider_id: str,
        configuration_set: str | None = None,
        client: Any | None = None,
    ) -> None:
        self._provider_id = provider_id
        self._configuration_set = configuration_set
        self._client = client

    def send(self, message: MailMessage) -> SendResult:
        client = self._client or _ses_client()
        body = {"Text": {"Data": message.text_body, "Charset": "UTF-8"}}
        if message.html_body:
            body["Html"] = {"Data": message.html_body, "Charset": "UTF-8"}
        request: dict[str, Any] = {
            "FromEmailAddress": message.sender.formatted(),
            "Destination": {"ToAddresses": [message.recipient.formatted()]},
            "Content": {
                "Simple": {
                    "Subject": {"Data": message.subject, "Charset": "UTF-8"},
                    "Body": body,
                }
            },
        }
        if message.reply_to:
            request["ReplyToAddresses"] = [message.reply_to.email]
        if self._configuration_set:
            request["ConfigurationSetName"] = self._configuration_set
        try:
            response = client.send_email(**request)
        except Exception as exc:
            raise ProviderError("ses send failed", retryable=True) from exc
        return SendResult(
            provider_id=self._provider_id,
            provider_type=ProviderType.SES,
            message_id=str(response["MessageId"]),
        )


def _ses_client() -> Any:
    import boto3  # type: ignore[import-not-found]

    return boto3.client("sesv2")
