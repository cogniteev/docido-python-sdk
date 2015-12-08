
from contextlib import closing
import pickle
import unittest

from docido_sdk.toolbox.file_ext import iterator_to_file
from docido_sdk.toolbox.http_ext import delayed_request


class TestStreamFromRequest(unittest.TestCase):
    def test_pickle(self):
        s = delayed_request('http://google.com')
        pickle.dumps(s)

    def test_fetch_google(self):
        with delayed_request('http://google.com').open() as istr:
            istr = iterator_to_file(iter(istr))
            all_content = content = istr.read(50)
            while len(content) == 50:
                content = istr.read(50)
                all_content += content
        self.assertTrue(all_content.endswith('</body></html>'))

        with delayed_request('http://google.com').open() as istr:
            istr = iterator_to_file(iter(istr))
            all_content_at_once = istr.read()
        self.assertTrue(all_content_at_once.endswith('</body></html>'))

    def test_iterate(self):
        content = ['foo', 'bar']
        result = []
        with closing(iterator_to_file(iter(content))) as istr:
            for word in istr:
                result.append(word)
        self.assertEqual(content, result)


if __name__ == '__main__':
    unittest.main()
