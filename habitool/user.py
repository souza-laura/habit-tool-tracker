import bcrypt
import random


def register(connection, firstname, lastname, username, password):
    """Function that allows to create / register a new acccount, by creating a new instance of the User class"""
    newuser = User()
    newuser.firstname = firstname
    newuser.lastname = lastname
    newuser.username = username
    newuser.password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    return newuser.create_user(connection)


def login(connection, username, password):
    """Function that allows to login / access an acccount.
    This function returns the user_id, that will be used for future operations."""
    userdbpassword = get_user_and_encrypted_pw(connection, username)
    if bcrypt.checkpw(password.encode('utf-8'), userdbpassword):
        return get_userid(connection, username)
    else:
        return -1


def change_username(connection, userid, newusername, password):
    """Function that allows to change the username"""
    existsnewusername = check_existing_username(connection, newusername)
    dbpassword = get_password(connection, userid)
    if bcrypt.checkpw(password.encode('utf-8'), dbpassword):
        if not existsnewusername:
            with connection:
                cur = connection.cursor()
                cur.execute("UPDATE user SET username=(?) WHERE user_id = (?)", (newusername, userid))
                return 1
        else:
            return -2
    else:
        return -1


def change_password(connection, userid, oldpassword, newpassword):
    """Function that allows to change the password"""
    dbpassword = get_password(connection, userid)
    newpassword = bcrypt.hashpw(newpassword.encode('utf-8'), bcrypt.gensalt())
    if bcrypt.checkpw(oldpassword.encode('utf-8'), dbpassword):
        with connection:
            cur = connection.cursor()
            cur.execute("UPDATE user SET password=(?) WHERE user_id = (?)", (newpassword, userid))
            return 1
    else:
        return -1


def delete_account(connection, userid):
    """Function that allows to delete an account"""
    with connection:
        cur = connection.cursor()
        cur.execute("DELETE FROM user WHERE user_id=(?)", (userid,))
        rowcount = cur.rowcount
        if rowcount:
            return rowcount
        else:
            return -1


def get_password(connection, userid):
    """User utility function that allows to get the password saved on the DB"""
    with connection:
        cur = connection.cursor()
        res = cur.execute("SELECT password FROM user WHERE user_id=(?)", (userid,)).fetchone()[0]
    return res


def get_firstname(connection, userid):
    """User utility function that allows to get the firstname saved on the DB"""
    with connection:
        cur = connection.cursor()
        res = cur.execute("SELECT first_name FROM user WHERE user_id=(?)", (userid,)).fetchone()[0]
    return res


def get_userid(connection, username):
    """User utility function that allows to get the user_id saved on the DB"""
    with connection:
        cur = connection.cursor()
        uid = cur.execute("SELECT user_id FROM user WHERE username=(?)", (username,)).fetchone()[0]
    return uid


def get_random_userid(connection):
    """User utility function for tests that allows to get a random user_id among those saved on the DB"""
    with connection:
        cur = connection.cursor()
        uidlist = cur.execute("SELECT user_id FROM user").fetchall()
        uid = -1
        if uidlist:
            uid = random.choice(uidlist)
        return uid


# TODO: delete this function if it's not useful
def get_username(connection, userid):
    with connection:
        cur = connection.cursor()
        username = cur.execute("SELECT username FROM user WHERE userid=(?)", (userid,)).fetchone()[0]
    return username


def check_existing_username(connection, username):
    """User utility function that allows to che if a username is already taken"""
    with connection:
        cur = connection.cursor()
        res = cur.execute("SELECT COUNT(*) FROM user WHERE username=(?)", (username,)).fetchone()[0]
    return res


def check_existing_uid(connection, userid):
    """User utility function that allows to che if a user_id exists."""
    with connection:
        cur = connection.cursor()
        res = cur.execute("SELECT COUNT(*) FROM user WHERE user_id=(?)", (userid,)).fetchone()[0]
    return res


def get_user_and_encrypted_pw(connection, username):
    exists = check_existing_username(connection, username)
    dbpassword = None
    if exists:
        userid = get_userid(connection, username)
        dbpassword = get_password(connection, userid)
    return dbpassword


# TODO: WRITE DOCUMENTATION OF USER CLASS
class User:
    """User class: this class has the purpose of creating a new user Object by creating an instance of this class."""
    def __int__(self, firstname, lastname, username, password):
        self.firstname = firstname
        self.lastname = lastname
        self.username = username
        self.password = password

    def create_user(self, connection):
        exists = check_existing_username(connection, self.username)
        if not exists:
            with connection:
                cur = connection.cursor()
                cur.execute("INSERT INTO user(first_name, last_name, username, password) VALUES (?,?,?,?)",
                            (self.firstname, self.lastname, self.username, self.password))
            return cur.lastrowid
        else:
            return -1
