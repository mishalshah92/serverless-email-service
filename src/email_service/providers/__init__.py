"""Email provider abstractions and adapters."""

from email_service.providers.base import MailProvider
from email_service.providers.factory import MailProviderFactory
from email_service.providers.ses import SesMailProvider
from email_service.providers.smtp import SmtpMailProvider

__all__ = ["MailProvider", "MailProviderFactory", "SesMailProvider", "SmtpMailProvider"]
