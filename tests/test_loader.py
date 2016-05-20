import unittest

from docido_sdk.toolbox.loader import resolve_name
from docido_sdk.toolbox.date_ext import timestamp_ms


class TestLoader(unittest.TestCase):
    def test_load_function(self):
        self.assertEqual(
            resolve_name,
            resolve_name('docido_sdk.toolbox.loader.resolve_name'))

    def test_load_class(self):
        self.assertEqual(
            timestamp_ms,
            resolve_name('docido_sdk.toolbox.date_ext.timestamp_ms'))

    def test_load_member_method(self):
        self.assertEqual(
            timestamp_ms.feeling_lucky,
            resolve_name('docido_sdk.toolbox.date_ext.timestamp_ms'
                         '.feeling_lucky')
        )
        self.assertEqual(
            timestamp_ms.now,
            resolve_name('docido_sdk.toolbox.date_ext.'
                         'timestamp_ms.now')
        )

    def test_load_module_variable(self):
        self.assertEqual(
            timestamp_ms.QUOTED_TIMEZONE,
            resolve_name('docido_sdk.toolbox.date_ext.'
                         'timestamp_ms.QUOTED_TIMEZONE'))

    def test_load_unknown_symbol(self):
        with self.assertRaises(ImportError):
            resolve_name('foo_module')

    def test_load_from_existing_symbol(self):
        self.assertEqual(
            timestamp_ms.feeling_lucky,
            resolve_name('feeling_lucky', timestamp_ms)
        )


if __name__ == '__main__':
    unittest.main()
