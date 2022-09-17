from user import checkexistinguid


def addnewhabit(connection, userid, habitname, habitdescription, periodicity, active):
    habit = Habit()
    habit.userid = userid
    habit.habitname = habitname
    habit.habitdescription = habitdescription
    habit.periodicity = periodicity
    habit.active = active
    habit.habittype = "USER"
    habitid = habit.createhabit(connection)
    return habitid


def deletehabit(connection, habitid):
    exists = habitexists(connection, habitid)
    if exists:
        with connection:
            cur = connection.cursor()
            cur.execute("DELETE FROM habit WHERE habit_id=(?)", (habitid,))
            rowcount = cur.rowcount
            if rowcount:
                return rowcount
    else:
        return -1


def getuserhabits(connection, userid):
    userhashabits = hashabits(connection, userid)
    if userhashabits:
        with connection:
            cur = connection.cursor()
            habits = cur.execute("SELECT habit_id, habit_name, habit_description, "
                                 "date(creation_date) as creation_date, periodicity, active FROM habit WHERE "
                                 "user_id=(?)", (userid,)).fetchall()
            return habits
    else:
        return userhashabits


def activate_deactivatehabit(connection, habitid):
    active = None
    if habitexists(connection, habitid):
        status = _getactivationstatus(connection, habitid)
        if status == -1:
            return status
        if status == 0:
            active = 1
        elif status == 1:
            active = 0
        with connection:
            cur = connection.cursor()
            cur.execute("UPDATE habit SET active=(?) WHERE habit_id = (?)", (active, habitid))


def modifyhabit(connection, habitid, columntoupdate, newvalue):
    query = f"UPDATE habit SET {columntoupdate}=" + f"'{newvalue}'" + f" WHERE habit_id = {habitid}"
    if habitexists(connection, habitid):
        with connection:
            cur = connection.cursor()
            cur.execute(query)
            query = f"SELECT {columntoupdate} from habit WHERE habit_id = {habitid}"
            modifiedvalue = cur.execute(query).fetchone()[0]
            if modifiedvalue.__eq__(f"{newvalue}"):
                print(query, newvalue)
                return 1
            else:
                return -1
    else:
        return -1


def _getactivationstatus(connection, habitid):
    if habitexists(connection, habitid):
        cur = connection.cursor()
        status = cur.execute("SELECT active FROM habit WHERE habit_id=(?)", (habitid,)).fetchone()[0]
        return status
    else:
        return -1


def habitexists(connection, habitid):
    with connection:
        cur = connection.cursor()
        habit = cur.execute("SELECT COUNT(*) FROM habit WHERE habit_id=(?)", (habitid,)).fetchone()[0]
        return habit


def hashabits(connection, userid):
    userexists = checkexistinguid(connection, userid)
    if userexists:
        with connection:
            cur = connection.cursor()
            habits = cur.execute("SELECT COUNT(*) FROM habit WHERE user_id=(?)", (userid,)).fetchone()[0]
            if habits > 0:
                return 1
            else:
                return -1


def markhabitascompleted(connection, habitid):
    with connection:
        cur = connection.cursor()
        cur.execute("INSERT INTO progress (habit_id, status) VALUES (?,?)", (habitid, 1))


def checkifalreadycompleted(connection, habitid, date):
    with connection:
        cur = connection.cursor()
        check = cur.execute("SELECT COUNT(*) FROM progress WHERE habit_id=(?) AND progress_date=(?) ", (habitid, date)).fetchone()[0]
        if check:
            return check
        else:
            return -1



def getpredefinedhabits(connection):
    with connection:
        cur = connection.cursor()
        habits = cur.execute("SELECT habit_name, habit_description, periodicity, type FROM predefined_habit").fetchall()
        return habits


def addpredefinedhabit(connection, userid, predefined: list):
    with connection:
        cur = connection.cursor()
        cur.execute("INSERT INTO habit(user_id, habit_name, habit_description, periodicity, active, type)"
                    "VALUES (?,?,?,?,?,?)", (userid, predefined[0], predefined[1], predefined[2], 1, predefined[3]))


class Habit:
    def __int__(self, userid, habitname, habitdescription, periodicity, active, habittype):
        self.userid = userid
        self.habitname = habitname
        self.habitdescription = habitdescription
        self.periodicity = periodicity
        self.active = active
        self.habittype = habittype

    def createhabit(self, connection):
        with connection:
            cur = connection.cursor()
            cur.execute("INSERT INTO habit(user_id, habit_name, habit_description, periodicity, active, type)"
                        "VALUES (?,?,?,?,?,?)",
                        (self.userid, self.habitname, self.habitdescription, self.periodicity, self.active,
                         self.habittype))
            return cur.lastrowid
