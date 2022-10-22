import random
import unittest

from faker import Faker

import test_utility

fake = Faker()
fake.name()
connection = test_utility.test_initialize_database('unittest.db')
periodicity = ["DAILY", "WEEKLY", "MONTHLY", "YEARLY"]
active = [0, 1]


def test_get_random_user_id():
    """User utility function for tests that allows to get a random user_id among those saved on the DB"""
    with connection:
        cur = connection.cursor()
        user_ids_list = cur.execute("SELECT user_id FROM user").fetchall()
        uid = -1
        if user_ids_list:
            uid = random.choice(user_ids_list)
        return uid


# TODO: complete unittests, add more tests if needed

class HabitTestCase(unittest.TestCase):
    def test_add_new_habit(self):
        user_random_id = test_get_random_user_id()
        newhabit = test_utility.test_add_new_habit(connection,
                                                   user_random_id[0],
                                                   fake.unique.word(),
                                                   fake.sentence(nb_words=6),
                                                   random.choice(periodicity),
                                                   random.choice(active))
        self.assertNotEqual(newhabit, -1)
        self.assertGreaterEqual(newhabit, 1)

    def test_mark_habit_as_completed(self):
        habit_id = test_utility.test_get_random_habit(connection)
        # for each habit I add 10 random dates of completion
        for n in range(7):
            res = test_utility.mark_habit_as_completed_tests(connection, habit_id,
                                                             fake.date_this_month())
        self.assertEqual(res, 1)
        self.assertNotEqual(res, -1)

    def test_delete_habit(self):
        deleted = test_utility.test_delete_habit(connection, 0)
        self.assertEqual(deleted, -1)
        habit_id = test_utility.test_get_random_habit_to_delete(connection)
        deleted = test_utility.test_delete_habit(connection, habit_id)
        self.assertEqual(deleted, 1)

    def test_get_habit_max_streak(self):
        habit_id = 13
        dates = test_utility.test_get_streak(connection, habit_id)
        habit_streak = test_utility.test_get_habit_max_streak(dates)
        self.assertGreaterEqual(habit_streak.size, 2)


if __name__ == '__main__':
    unittest.main()
