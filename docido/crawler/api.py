
from collections import namedtuple

from docido.core import Interface

class ICrawlerManager(Interface):
    """Extension point interface for components willing to
    provide crawl configurations.
    """

    def get_crawler_configuration(name):
        """
        :return:
          crawl configuration of the given `name`, `None` otherwise.
        :rtype: CrawlConfiguration
        """
        pass

class CrawlConfiguration(namedtuple(
    'CrawlerConfiguration',
    [
        "base_url",
        "access_token_url",
        "authorize_url",
        "access_token_method",
        "request_token_params",
        "consumer_key",
        "consumer_secret",
    ]
)):
    """Configuration passed to a crawl session

    :ivar string base_url: service base URL
    :ivar string access_token_url: suffix URL to retrieve an OAuth token
    :ivar string authorize_url: suffix URL to ask for an OAuth token
    :ivar dict request_token_params: additional HTTP parameters passed
          when requesting a token.
    :ivar consumer_key: Docido consumer key of the given service
    :ivar consumer_secret: Docido consumer secret of the given service
    """

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

        :param docido.crawler.oauth.OAuthToken oauth_token:
          OAuth credentials

        :return: user account identifier
        :rtype: string
        """

    def handle_oauth_response(oauth):
        """Handle the OAuth response with the proper method,
        and extract meaningful fields from response.

        :param flask_oauthlib.client.OAuth oauth: OAuth transaction
        :rtype: docido.crawler.oauth.OAuthToken
        """
