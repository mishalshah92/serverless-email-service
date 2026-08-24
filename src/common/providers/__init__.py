"""Email provider abstractions and adapters."""

from common.providers.base import MailProvider
from common.providers.factory import MailProviderFactory
from common.providers.ses import SesMailProvider
from common.providers.smtp import SmtpMailProvider

__all__ = ["MailProvider", "MailProviderFactory", "SesMailProvider", "SmtpMailProvider"]
