import random

import numpy as np

from habitool import database


# unfortunately, had to duplicate functions and class in order to avoid import problems (couldn't solve them)

def test_initialize_database(db_name):
    connection = database.connect(db_name)
    cur = connection.cursor()
    # Check if the table exists
    exists = cur.execute("""SELECT count(*)
                            FROM sqlite_master
                            WHERE type='table' 
                            AND name='predefined_habit';""").fetchone()[0]
    if not exists:
        with connection:
            # Initialize database by executing all queries in this file
            with open('../dbinitialization.txt') as initializer:
                for command in initializer:
                    cur.execute(command)
            initializer.close()
    return connection


def test_check_habit_progress_mark_habit_as_complete(connection, habit_id):
    with connection:
        cur = connection.cursor()
        check = cur.execute("SELECT COUNT(*) FROM progress WHERE habit_id=(?)", (habit_id,)).fetchone()
        if check >= 1:
            return 1
        else:
            return -1


def test_check_habit_progress_get_streak(connection, habit_id):
    with connection:
        cur = connection.cursor()
        check = cur.execute("SELECT COUNT(*) FROM progress WHERE habit_id=(?)", (habit_id,)).fetchone()
        if int(check[0]) >= 1:
            return 1
        else:
            return -1


def test_get_streak(connection, habit_id):
    check = test_check_habit_progress_get_streak(connection, habit_id)
    with connection:
        connection.row_factory = lambda cursor, row: row[0]
        cur = connection.cursor()
        if check:
            dates = cur.execute("SELECT progress_date FROM progress WHERE habit_id=(?) ORDER BY progress_date",
                                (habit_id,)).fetchall()
            return dates

        else:
            return check


def test_get_random_habit(connection):
    with connection:
        cur = connection.cursor()
        habit_id_list = cur.execute("SELECT habit_id FROM habit WHERE habit_id <= 25").fetchall()
        habit_id = -1
        if habit_id_list:
            habit_id = random.choice(habit_id_list)
        return str(habit_id)


def test_get_random_habit_to_delete(connection):
    with connection:
        cur = connection.cursor()
        habit_id_list = cur.execute("SELECT habit_id FROM habit WHERE habit_id > 25").fetchall()
        habit_id_list = [r[0] for r in habit_id_list]
        habit_id = -1
        if habit_id_list:
            habit_id = random.choice(habit_id_list)
        return str(habit_id)


def test_get_random_username_to_delete(connection):
    with connection:
        cur = connection.cursor()
        username_list = cur.execute("SELECT username FROM main.user WHERE user.user_id > 15").fetchall()
        username = -1
        if username_list:
            username = random.choice(username_list)
        return username


def test_has_habits(connection, user_id):
    user_exists = test_check_existing_uid(connection, user_id)
    if user_exists:
        with connection:
            cur = connection.cursor()
            habits = cur.execute("SELECT COUNT(*) FROM habit WHERE user_id=(?)", (user_id,)).fetchone()[0]
            if habits > 0:
                return 1
            else:
                return -1


def mark_habit_as_completed_tests(connection, habit_id, completion_date):
    with connection:
        cur = connection.cursor()
        cur.execute("INSERT INTO progress (habit_id, progress_date,status) VALUES (?,?,?)",
                    (habit_id, completion_date, 1))
        rowcount = cur.rowcount
        if rowcount:
            return rowcount
        else:
            return -1


def test_check_existing_uid(connection, user_id):
    with connection:
        cur = connection.cursor()
        res = cur.execute("SELECT COUNT(*) FROM user WHERE user_id=(?)", (user_id,)).fetchone()[0]
    return res


def test_delete_habit(connection, habit_id):
    with connection:
        cur = connection.cursor()
        cur.execute("DELETE FROM habit WHERE habit_id=(?)", (habit_id,))
        rowcount = cur.rowcount
        if rowcount:
            return rowcount
        else:
            return -1


def test_get_habit_max_streak(dates_list: list):
    np_dates = np.array(dates_list, dtype='datetime64[D]')
    i0max, i1max = 0, 0
    i0 = 0
    for i1, date in enumerate(np_dates):
        if date - np_dates[i0] != np.timedelta64(i1 - i0, 'D'):
            if i1 - i0 > i1max - i0max:
                i0max, i1max = i0, i1
            i0 = i1
    return np_dates[i0max:i1max]


def test_add_new_habit(connection, user_id, habit_name, habit_description, periodicity, active):
    habit = TestHabit()
    habit.user_id = user_id
    habit.habitname = habit_name
    habit.habitdescription = habit_description
    habit.periodicity = periodicity
    habit.active = active
    habit.habittype = "USER"
    habit_id = habit.create_habit(connection)
    return habit_id


class TestHabit:
    def __int__(self, user_id, habitname, habitdescription, periodicity, active, habittype):
        self.user_id = user_id
        self.habitname = habitname
        self.habitdescription = habitdescription
        self.periodicity = periodicity
        self.active = active
        self.habittype = habittype

    def create_habit(self, connection):
        with connection:
            cur = connection.cursor()
            cur.execute("INSERT INTO habit(user_id, habit_name, habit_description, periodicity, active, type)"
                        "VALUES (?,?,?,?,?,?)",
                        (self.user_id, self.habitname, self.habitdescription, self.periodicity, self.active,
                         self.habittype))
            return cur.lastrowid
