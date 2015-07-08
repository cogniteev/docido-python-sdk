
from docido_sdk.core import Interface

__all__ = [
    'IOAuthProvider',
    'OAuthToken',
    'OAuthExpiresToken',
    'OAuthRefreshToken',
    'OAuthSecretToken',
]

class IOAuthProvider(Interface):
    def refresh_token():
        """Refresh the OAuth token

        :return: the new OAuth token
        :rtype: string
        """
        pass


class OAuthToken(object):
    """OAuth credentials base-class. Several implementations are available:

    this class:
      for simple authentication using only *access token*

    :py:class:`docido.oauth.api.OAuthExpiresToken` :
      when *access token* expires after some time

    :py:class:`docido.oauth.api.OAuthRefreshToken` :
      when *access token* is short-lived and a *refresh token* is provided
      to re-create it.

    :py:class:`docido.oauth.api.OAuthSecretToken` :
      when authentication does not use consumer keys but thru a pair
      of keys given during OAuth negotiation.
    """
    def __init__(self, access_token):
        """
        :param string access_token:
            OAuth granted access token used by Docido to gain access
            to the protected resources on behalf of the user, instead
            of using the User's Service Provider credentials.
        """
        self.__access_token = access_token

    access_token = property(
        fget=lambda slf: slf.__access_token,
        doc='''Read-only property accessor over the
        OAuth granted access token

        :rtype: string
        '''
    )


class OAuthExpiresToken(OAuthToken):
    def __init__(self, access_token, expires_in):
        """
        :param int expires_in:
            Number of days the token will be valid for.
        """
        super(OAuthExpiresToken, self).__init__(access_token)
        self.__expires_in = expires_in

    expires_in = property(
        fget=lambda slf: slf.__expires_in,
        doc='''Read-only property accessor over the
        number of days the token will be valid for.

        :rtype: int
        '''
    )


class OAuthRefreshToken(OAuthToken):
    def __init__(self, access_token, refresh_token):
        """
        :param string refresh_token:
            OAuth refresh token used to recreate the access token
        """
        super(OAuthRefreshToken, self).__init__(access_token)
        self.__refresh_token = refresh_token

    refresh_token = property(
        fget=lambda slf: slf.__refresh_token,
        doc='''Read-only property accessor over the
        OAuth refresh token used to recreate the access token.

        :rtype: string
        '''
    )


class OAuthSecretToken(OAuthToken):
    def __init__(self, access_token, token_secret):
        """
        :param string token_secret:
            secret used by Docido to establish ownership
            of a given access token.
        """
        super(OAuthSecretToken, self).__init__(access_token)
        self.__token_secret = token_secret

    token_secret = property(
        fget=lambda slf: slf.__token_secret,
        doc='''Read-only property accessor over the
        secret used by Docido to establish ownership of
        a given access token.

        :rtype: string
        '''
    )
