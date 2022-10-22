import unittest

from faker import Faker

import test_utility
from habitool import user

fake = Faker()
fake.name()
connection = test_utility.test_initialize_database('unittest.db')


class UserTestCase(unittest.TestCase):
    def test_registration(self):
        uuid = user.register(connection, fake.unique.first_name(), fake.unique.last_name(), fake.unique.user_name(),
                             "password")
        self.assertNotEqual(uuid, -1)
        self.assertGreater(uuid, -1)
        uuid = user.register(connection, "Paolo", "Rossi", "laurabianchi", "password")
        self.assertEqual(uuid, -1)

    def test_login(self):
        uuid = user.login(connection, "laurabianchi", "password")
        self.assertNotEqual(uuid, -1)
        uuid = user.login(connection, "laurabianchi", "repsord")
        self.assertEqual(uuid, -1)

    def test_change_username(self):
        uuid = 8
        result = user.change_username(connection, uuid, "gibsondonald", "password")
        self.assertEqual(result, -2)
        result = user.change_username(connection, uuid, fake.unique.user_name(), "drowssap")
        self.assertNotEqual(result, 1)
        result = user.change_username(connection, uuid, fake.unique.user_name(), "password")
        self.assertEqual(result, 1)

    def test_change_password(self):
        uuid = user.get_user_id(connection, "martinezjamie")
        result = user.change_password(connection, uuid, "repsord", "password")
        self.assertNotEqual(result, 1)
        self.assertEqual(result, -1)
        # I'm not actually going to change the password so that I can keep doing the tests
        result = user.change_password(connection, uuid, "password", "password")
        self.assertEqual(result, 1)

    def test_delete_account(self):
        username = test_utility.test_get_random_username_to_delete(connection)[0]
        print(username)
        uuid = user.get_user_id(connection, username)
        result = user.delete_account(connection, 0)
        self.assertEqual(result, -1)
        result = user.delete_account(connection, uuid)
        self.assertNotEqual(result, -1)
        self.assertEqual(result, 1)


if __name__ == '__main__':
    unittest.main()
