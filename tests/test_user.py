import unittest
import user
import sqlite3

connection = sqlite3.connect('/Users/lauradealmeidasouza/development/habit-tool-tracker/test.db')


class UserTestCase(unittest.TestCase):
    def test_registration(self):
        uuid = user.register(connection, "Laura", "Bianchi", "laurabianchi", "password".encode('utf-8'))
        self.assertNotEqual(uuid, -1)  # add assertion here


if __name__ == '__main__':
    unittest.main()
