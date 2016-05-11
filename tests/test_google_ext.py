import unittest

from docido_sdk.toolbox.google_ext import (
    OAuthToken,
    OAuthTokenExpiredError,
    OAuthTokenRefreshRequiredError,
    refresh_token,
    token_info,
)

from utils import vcr


class GoogleExt(unittest.TestCase):
    EXPIRED_TOKEN = OAuthToken(
        access_token='expired_token',
        refresh_token='refresh_token42',
        consumer_key='consumer_key42',
        consumer_secret='consumer_secret42',
    )

    @vcr.use_cassette
    def test_refresh_token(self):
        token = OAuthToken(
            refresh_token='refresh_token42',
            consumer_secret='consumer_secret42',
            consumer_key='consumer_key42'
        )
        new_token = refresh_token(token)
        self.assertEqual(
            new_token.access_token,
            'access_token42'
        )

    @vcr.use_cassette
    def test_refresh_invalid_client(self):
        token = OAuthToken(
            refresh_token='refresh_token41',
            consumer_secret='consumer_secret41',
            consumer_key='consumer_key41'
        )
        self._refresh_error_scenario(
            token,
            u'invalid_client: The OAuth client was not found.'
        )

    @vcr.use_cassette
    def test_refresh_invalid_refresh_token(self):
        token = OAuthToken(
            access_token='access_token42',
            refresh_token='refresh_token41',
            consumer_secret='consumer_secret42',
            consumer_key='consumer_key42',
        )
        self._refresh_error_scenario(
            token,
            u'invalid_grant'
        )

    @vcr.use_cassette
    def test_token_info(self):
        token = OAuthToken(access_token='access_token42')
        self._validate_token_info(token_info(token), expected_refresh=False)

    @vcr.use_cassette
    def test_token_info_refresh_no_cb(self):
        self._validate_token_info(token_info(self.EXPIRED_TOKEN))

    @vcr.use_cassette
    def test_token_info_refresh_cb(self):
        cb_called = [False]

        def refresh_cb(token):
            self.assertEqual(token.access_token, 'access_token42')
            cb_called[0] = True
        info = token_info(self.EXPIRED_TOKEN, refresh_cb=refresh_cb)
        self._validate_token_info(info)

    @vcr.use_cassette
    def test_token_info_refresh_cb_error(self):
        cb_called = [False]

        def refresh_cb(token):
            self.assertEqual(token.access_token, 'access_token42')
            cb_called[0] = True
            raise Exception('eat that!')
        info = token_info(self.EXPIRED_TOKEN, refresh_cb=refresh_cb)
        self._validate_token_info(info)

    @vcr.use_cassette
    def test_token_info_no_refresh(self):
        with self.assertRaises(OAuthTokenRefreshRequiredError):
            token_info(self.EXPIRED_TOKEN, refresh=False)

    def _validate_token_info(self, info, expected_refresh=True):
        self.assertEqual(
            info.pop('scope'),
            set(['scope1', 'scope2', 'scope3'])
        )
        info.pop('token', None)
        self.assertEqual(
            info,
            dict(email_verified=True, azp='azp42', access_type='offline',
                 email='tech@cogniteev.com', refreshed=expected_refresh,
                 exp=1463043859, sub='sub42', aud='aud42',
                 expires_in=3512)
        )

    def _refresh_error_scenario(self, token, expected_message):
        with self.assertRaises(OAuthTokenExpiredError) as exc:
            refresh_token(token)
        self.assertEqual(exc.exception.message, expected_message)


if __name__ == '__main__':
    unittest.main()
