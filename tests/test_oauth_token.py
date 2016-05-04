import unittest

from docido_sdk.oauth import OAuthToken


class TestOAuthToken(unittest.TestCase):
    def test_create_oauth_token(self):
        token = OAuthToken(
            access_token=1,
            refresh_token=2,
            token_secret=3,
            consumer_key=4,
            expires=5
        )
        self.assertEqual(1, token.access_token)
        self.assertEqual(2, token.refresh_token)
        self.assertEqual(3, token.token_secret)
        self.assertEqual(4, token.consumer_key)
        self.assertEqual(5, token.expires)


if __name__ == '__main__':
    unittest.main()
