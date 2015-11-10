import pickle
import unittest

from docido_sdk.toolbox.file_ext import stream_from_request


class TestStreamFromRequest(unittest.TestCase):
    def test_pickle(self):
        s = stream_from_request('http://google.com')
        pickle.dumps(s)

    def test_fetch_google(self):
        with stream_from_request('http://google.com').open() as istr:
            all_content = content = istr.read(50)
            while len(content) == 50:
                content = istr.read(50)
                all_content += content
        self.assertTrue(all_content.endswith('</body></html>'))

        with stream_from_request('http://google.com').open() as istr:
            all_content_at_once = istr.read()
        self.assertTrue(all_content_at_once.endswith('</body></html>'))


if __name__ == '__main__':
    unittest.main()
