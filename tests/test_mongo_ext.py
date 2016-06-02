import os
import unittest

from docido_sdk.toolbox.mongo_ext import MongoClientPool


class MongoExt(unittest.TestCase):
    MONGO_HOST = os.environ.get('MONGO_HOST', 'localhost')

    def test_connect_twice(self):
        con1 = MongoClientPool.get(host=self.MONGO_HOST)
        con2 = MongoClientPool.get(host=self.MONGO_HOST)
        self.assertEqual(
            hash(con1),
            hash(con2)
        )
        self.assertEqual(
            con1.admin.command('ping'),
            dict(ok=1.0)
        )

    def test_connect_change_parameters(self):
        con1 = MongoClientPool.get(host=self.MONGO_HOST)
        con2 = MongoClientPool.get(host=self.MONGO_HOST, max_pool_size=42)
        con3 = MongoClientPool.get(host=self.MONGO_HOST)
        self.assertNotEqual(hash(con1), hash(con2))
        self.assertEqual(hash(con1), hash(con3))
        self.assertEqual(
            con1.admin.command('ping'),
            dict(ok=1.0)
        )
        self.assertEqual(con1.max_pool_size, 100)
        self.assertEqual(con2.max_pool_size, 42)


if __name__ == '__main__':
    unittest.main()
