import unittest

from docido_sdk.core import (
    Component,
    ExtensionPoint,
    implements,
    Interface,
)
from docido_sdk.env import Environment


class Foobar(Interface):
    pass


class FooInterface(Interface):
    def foo():
        pass


class FooComponent(Component):
    implements(FooInterface, Foobar)


class BarInterface(Interface):
    pass


class BarComponent(Component):
    implements(BarInterface, Foobar)


class Pika(Interface):
    pass


class TestCore(unittest.TestCase):
    def test_expect_1_when_0(self):
        class expect_one_pika(Component):
            pika = ExtensionPoint(Pika, unique=True)
        env = Environment()
        consumer = env[expect_one_pika]
        with self.assertRaises(Exception) as exc:
            consumer.pika
        self.assertEqual(
            exc.exception.message,
            "Expected one 'Pika' component, but found 0"
        )

    def test_expect_1_when_more(self):
        class expect_one_foobar(Component):
            foobar = ExtensionPoint(Foobar, unique=True)
        env = Environment()
        consumer = env[expect_one_foobar]
        with self.assertRaises(Exception) as exc:
            consumer.foobar
        self.assertEqual(
            exc.exception.message,
            "Expected one 'Foobar' component, but found 2: "
            "BarComponent, FooComponent"
        )


if __name__ == '__main__':
    unittest.main()
