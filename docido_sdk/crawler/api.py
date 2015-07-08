
from collections import namedtuple

from docido.core import Interface

__all__ = [
    'ICrawler',
]

class ICrawler(Interface):
    """Extension point interface for components willing to
    provide additional Docido crawlers.
    """
    def get_service_name():
        """
        :return: crawler name
        :rtype: string
        """

    def get_account_login(oauth_token):
        """Provides most *human-readable* representation of the
        user account. The returned value is used to identify
        the account among others.

        :param docido.oauth.OAuthToken oauth_token:
          OAuth credentials

        :return: user account identifier
        :rtype: string
        """

#    def handle_oauth_response(oauth):
#        """Handle the OAuth response with the proper method,
#        and extract meaningful fields from response.
#
#        :param flask_oauthlib.client.OAuth oauth: OAuth transaction
#        :rtype: docido.crawler.oauth.OAuthToken
#        """

    def iter_crawl_tasks(papi, oauth_token, full=False):
        """Split the crawl in smaller independant actions,
        and returns them instead of executing them.

        :param docido.push.api.PushAPI

        :param basestring oauth_token:
          OAuth credentials

        :param bool full:
          whether the entire account must be pushed or only
          changes that occured since previous crawl.

        :return: generator of `py:class:`functools.partial` objects
                 to execute to perform the crawl.
                 a tuple can also be returns for crawlers that needs
                 to perform a final operation when partial objects
                 have been executed:
                 `tuple(generator of partial, partial)`
                 Partial instances may accept 2 arguments:
                   - push_api - docido.push.api.PushAPI
                   - token - basestring

        """



    def clear_account(oauth_token):
        """Remove from Docido index all data previously indexed for
        this account. Persisted data must also be cleared.

        :param docido.crawler.oauth.OAuthToken oauth_token:
          OAuth credentials
        """
