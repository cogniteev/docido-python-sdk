import unittest

from docido_sdk.toolbox.ha import RetryDelaySeries, HA


class TestHA(unittest.TestCase):
    def test_teb_policy(self):
        teb = RetryDelaySeries.get(
            'truncated_exponential_backoff',
            max_collisions=5,
            delay=10)
        self.assertEquals(next(teb), 0)
        self.assertIn(next(teb), [0, 10])
        self.assertIn(next(teb), [0, 10, 20])
        self.assertIn(next(teb), [0, 10, 20, 30])
        self.assertIn(next(teb), [0, 10, 20, 30, 40])
        self.assertEquals(next(teb), 0)

    def test_linear_policy(self):
        linear = RetryDelaySeries.get(
            'linear',
            delay=10, max_delay=100, step=40
        )
        self.assertEquals(next(linear), 10)
        self.assertEquals(next(linear), 50)
        self.assertEquals(next(linear), 90)
        self.assertEquals(next(linear), 100)
        self.assertEquals(next(linear), 100)

        # No stop
        linear = RetryDelaySeries.get(
            'linear',
            delay=10, step=40
        )
        self.assertEquals(next(linear), 10)
        self.assertEquals(next(linear), 50)
        self.assertEquals(next(linear), 90)
        self.assertEquals(next(linear), 130)
        self.assertEquals(next(linear), 170)

    def test_ha(self):
        test_instance = self
        call_count = [0]

        class Foo(HA):
            def __init__(self):
                super(Foo, self).__init__()
                self.ha_config.default.delay = 0

            @HA.catch(RuntimeError)
            def method(self, counter):
                if counter != 0:
                    raise RuntimeError()
                return 0

            def ha_on_error(self, method, exc, args, kwargs):
                test_instance.assertIsInstance(exc, RuntimeError)
                counter = args[0]
                test_instance.assertIsInstance(counter, int)
                call_count[0] += 1
                return (counter - 1,), {}

        foo = Foo()
        self.assertEqual(foo.method(3), 0)

    def test_ha_max_retries(self):
        call_count = [0]

        class Foo(HA):
            def __init__(self):
                super(Foo, self).__init__()
                self.ha_config.default.delay = 0
                self.ha_config.default.max_retries = 2

            @HA.catch(RuntimeError)
            def method(self):
                call_count[0] += 1
                raise RuntimeError()

        foo = Foo()
        with self.assertRaises(RuntimeError):
            foo.method()
        self.assertEqual(call_count[0], 3)
