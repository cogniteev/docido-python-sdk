"""
Provides a set of Exception classes a crawler may raise when it is
not possible to consume source API because of OAuth-related issues.
"""

from .. core import DocidoError


class CrawlerError(DocidoError):
    """Common base exception class for crawl issues"""
    def __init__(self, message=None):
        """
        @param message: optional printable object providing
          reason for error.
        """
        super(CrawlerError, self).__init__(message)


class OAuthTokenExpiredError(CrawlerError):
    """Exception class used to notify crawler manager when
    the OAuth token of an account has expired, and needs to be refreshed
    thru Docido front application.
    """
    def __init__(self, message=None):
        """
        @param message: optional printable object providing
          the error message returned by source API.
        """
        super(OAuthTokenExpiredError, self).__init__(message)


class OAuthTokenPermanentError(CrawlerError):
    """Exception class used to notify crawler manager when
    the OAuth token of an account has been revoked.
    """
    def __init__(self, message=None):
        """
        @param message: optional printable object providing
          the error message returned by source API.
        """
        super(OAuthTokenPermanentError, self).__init__(message)


class OAuthTokenRefreshRequiredError(CrawlerError):
    """Exception class used to notify crawler manager when
    the OAuth token of an account has expired or will expire
    shortly, and need to be refreshed programmaticaly.
    """
    def __init__(self, message=None):
        """
        @param message: optional printable object providing
          the error message returned by source API.
        """
        super(OAuthTokenRefreshRequiredError, self).__init__(message)
