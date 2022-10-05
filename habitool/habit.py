from habitool.user import check_existing_uid
import random


def add_new_habit(connection, user_id, habitname, habitdescription, periodicity, active):
    """Function that allows to create a new habit, by creating a new instance of the Habit class"""
    habit = Habit()
    habit.user_id = user_id
    habit.habitname = habitname
    habit.habitdescription = habitdescription
    habit.periodicity = periodicity
    habit.active = active
    habit.habittype = "USER"
    habit_id = habit.create_habit(connection)
    return habit_id


def delete_habit(connection, habit_id):
    """Function that allows to delete a habit from the Db"""
    exists = habit_exists(connection, habit_id)
    if exists:
        with connection:
            cur = connection.cursor()
            cur.execute("DELETE FROM habit WHERE habit_id=(?)", (habit_id,))
            rowcount = cur.rowcount
            if rowcount:
                return rowcount
    else:
        return -1


def get_random_habit(connection):
    """Utility function for tests that allows to get a random habit from the Db"""
    with connection:
        cur = connection.cursor()
        habit_idlist = cur.execute("SELECT user_id FROM user").fetchall()
        habit_id = -1
        if habit_idlist:
            habit_id = random.choice(habit_idlist)
        return habit_id[0]


def get_user_habits(connection, user_id):
    """Function that allows to get all habits that belong to a specific user."""
    userhashabits = has_habits(connection, user_id)
    if userhashabits:
        with connection:
            cur = connection.cursor()
            habits = cur.execute("SELECT habit_id, habit_name, habit_description, "
                                 "date(creation_date) as creation_date, periodicity, active FROM habit WHERE "
                                 "user_id=(?)", (user_id,)).fetchall()
            return habits
    else:
        return userhashabits


def get_active_user_habits(connection, user_id):
    """Function that allows to get all active habits that belong to a specific user."""
    userhashabits = has_habits(connection, user_id)
    if userhashabits:
        with connection:
            cur = connection.cursor()
            habits = cur.execute("SELECT habit_id, habit_name, habit_description, "
                                 "date(creation_date) as creation_date, periodicity, active FROM habit WHERE "
                                 "user_id=(?) AND active = 1", (user_id,)).fetchall()
            return habits
    else:
        return userhashabits


def get_user_habits_for_streak(connection, user_id):
    """Function that allows to get DAILY and ACTUVE habits that belong to a specific user.
    For these habits will be available the option to view the MAX streak."""
    with connection:
        cur = connection.cursor()
        habits = cur.execute("SELECT habit_id, habit_name, habit_description, "
                             "date(creation_date) as creation_date, periodicity, active FROM habit WHERE "
                             "user_id=(?) AND periodicity = 'DAILY' AND active = 1", (user_id,)).fetchall()
    if habits:
        return habits
    else:
        return -1


def get_filtered_habits(connection, user_id, filterval, column='periodicity'):
    """Function that allows to get filtered (active, non-active, DAILY, WEEKLY, MONTHLY) habits for habit analysis that belong to a specific user.
    For these habits will be available the option to view the MAX streak."""

    query = f"SELECT habit_id, habit_name, habit_description, date(creation_date) as creation_date, periodicity, active FROM habit WHERE user_id = {user_id} AND {column} = {filterval}"
    with connection:
        cur = connection.cursor()
        habits = cur.execute(query).fetchall()

    if habits:
        return habits
    else:
        return -1


def activate_deactivate_habit(connection, habit_id):
    """Function that allows activate or deactivate habits that belong to a specific user."""

    active = None
    if habit_exists(connection, habit_id):
        status = _getactivationstatus(connection, habit_id)
        if status == -1:
            return status
        if status == 0:
            active = 1
        elif status == 1:
            active = 0
        with connection:
            cur = connection.cursor()
            cur.execute("UPDATE habit SET active=(?) WHERE habit_id = (?)", (active, habit_id))


def modify_habit(connection, habit_id, columntoupdate, newvalue):
    """Function that allows to modify a habit's property"""

    query = f"UPDATE habit SET {columntoupdate}=" + f"'{newvalue}'" + f" WHERE habit_id = {habit_id}"
    if habit_exists(connection, habit_id):
        with connection:
            cur = connection.cursor()
            cur.execute(query)
            query = f"SELECT {columntoupdate} from habit WHERE habit_id = {habit_id}"
            modifiedvalue = cur.execute(query).fetchone()[0]
            if modifiedvalue.__eq__(f"{newvalue}"):
                return 1
            else:
                return -1
    else:
        return -1


def _getactivationstatus(connection, habit_id):
    """Utility function that allows to get the activation status of a habit."""
    if habit_exists(connection, habit_id):
        cur = connection.cursor()
        status = cur.execute("SELECT active FROM habit WHERE habit_id=(?)", (habit_id,)).fetchone()[0]
        return status
    else:
        return -1


def habit_exists(connection, habit_id):
    """Utility function that allows to check if a habit exists."""
    with connection:
        cur = connection.cursor()
        habit = cur.execute("SELECT COUNT(*) FROM habit WHERE habit_id=(?)", (habit_id,)).fetchone()[0]
        return habit


def has_habits(connection, user_id):
    """Utility function that allows to check if the user has any habits"""
    userexists = check_existing_uid(connection, user_id)
    if userexists:
        with connection:
            cur = connection.cursor()
            habits = cur.execute("SELECT COUNT(*) FROM habit WHERE user_id=(?)", (user_id,)).fetchone()[0]
            if habits > 0:
                return 1
            else:
                return -1


def mark_habit_as_completed(connection, habit_id):
    """Utility function that allows to check if the user has any habits"""
    with connection:
        cur = connection.cursor()
        cur.execute("INSERT INTO progress (habit_id, status) VALUES (?,?)", (habit_id, 1))


def mark_habit_as_completed_tests(connection, habit_id, completiondate):
    """Utility function for tests that allows to mark a habit as completed at a specific day (random dates)"""
    with connection:
        cur = connection.cursor()
        cur.execute("INSERT INTO progress (habit_id, progress_date,status) VALUES (?,?,?)",
                    (habit_id, completiondate, 1))
        rowcount = cur.rowcount
        if rowcount:
            return rowcount
        else:
            return -1


def get_streak(connection, habit_id):
    """Function that allows to get the completion streak of a habit. (at the moment, only available for DAILY and ACTIVE habits)"""
    check = check_habit_progress(connection, habit_id)
    with connection:
        connection.row_factory = lambda cursor, row: row[0]
        cur = connection.cursor()
        if check:
            dates = cur.execute("SELECT progress_date FROM progress WHERE habit_id=(?) ORDER BY progress_date", (habit_id,)).fetchall()
            return dates
        else:
            return check


def check_habit_progress(connection, habit_id):
    """Function that allows to check if the habit has any progress at all (if the habit was ever marked as completed)"""
    with connection:
        cur = connection.cursor()
        check = cur.execute("SELECT COUNT(*) FROM progress WHERE habit_id=(?)", (habit_id,)).fetchone()[0]
        if check == 1 or check > 1:
            return 1
        else:
            return -1


def check_if_already_completed(connection, habit_id, date):
    """Utility function that allows to check if a habit was already completed on the current date"""

    with connection:
        cur = connection.cursor()
        check = cur.execute("SELECT COUNT(*) FROM progress WHERE habit_id=(?) AND progress_date=(?) ",
                            (habit_id, date)).fetchone()[0]
        if check:
            return check
        else:
            return -1


def get_predefined_habits(connection):
    """Function that allows to get predefined habits from the DB)"""
    with connection:
        cur = connection.cursor()
        habits = cur.execute("SELECT habit_name, habit_description, periodicity, type FROM predefined_habit").fetchall()
        return habits


def add_predefined_habit(connection, user_id, predefined: list):
    """Function that allows to add predefined habits"""
    with connection:
        cur = connection.cursor()
        cur.execute("INSERT INTO habit(user_id, habit_name, habit_description, periodicity, active, type)"
                    "VALUES (?,?,?,?,?,?)", (user_id, predefined[0], predefined[1], predefined[2], 1, predefined[3]))


class Habit:
    """Habit class: this class has the purpose of creating a new habit Object by creating an instance of this class."""
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
