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
    user_db_password = get_user_and_encrypted_pw(connection, username)
    if bcrypt.checkpw(password.encode('utf-8'), user_db_password):
        return get_user_id(connection, username)
    else:
        return -1


def change_username(connection, user_id, newusername, password):
    """Function that allows to change the username"""
    exists_new_username = check_existing_username(connection, newusername)
    db_password = get_password(connection, user_id)
    if bcrypt.checkpw(password.encode('utf-8'), db_password):
        if not exists_new_username:
            with connection:
                cur = connection.cursor()
                cur.execute("UPDATE user SET username=(?) WHERE user_id = (?)", (newusername, user_id))
                return 1
        else:
            return -2
    else:
        return -1


def change_password(connection, user_id, old_password, new_password):
    """Function that allows to change the password"""
    db_password = get_password(connection, user_id)
    new_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
    if bcrypt.checkpw(old_password.encode('utf-8'), db_password):
        with connection:
            cur = connection.cursor()
            cur.execute("UPDATE user SET password=(?) WHERE user_id = (?)", (new_password, user_id))
            return 1
    else:
        return -1


def delete_account(connection, user_id):
    """Function that allows to delete an account"""
    with connection:
        cur = connection.cursor()
        cur.execute("DELETE FROM user WHERE user_id=(?)", (user_id,))
        rowcount = cur.rowcount
        if rowcount:
            return rowcount
        else:
            return -1


def get_password(connection, user_id):
    """User utility function that allows to get the password saved on the DB"""
    with connection:
        cur = connection.cursor()
        res = cur.execute("SELECT password FROM user WHERE user_id=(?)", (user_id,)).fetchone()[0]
    return res


def get_firstname(connection, user_id):
    """User utility function that allows to get the firstname saved on the DB"""
    with connection:
        cur = connection.cursor()
        res = cur.execute("SELECT first_name FROM user WHERE user_id=(?)", (user_id,)).fetchone()[0]
    return res


def get_user_id(connection, username):
    """User utility function that allows to get the user_id saved on the DB"""
    with connection:
        cur = connection.cursor()
        uid = cur.execute("SELECT user_id FROM user WHERE username=(?)", (username,)).fetchone()[0]
    return uid


def get_random_user_id(connection):
    """User utility function for tests that allows to get a random user_id among those saved on the DB"""
    with connection:
        cur = connection.cursor()
        user_ids_list = cur.execute("SELECT user_id FROM user").fetchall()
        uid = -1
        if user_ids_list:
            uid = random.choice(user_ids_list)
        return uid


def get_username(connection, user_id):
    with connection:
        cur = connection.cursor()
        username = cur.execute("SELECT username FROM user WHERE user_id=(?)", (user_id,)).fetchone()[0]
    return username


def check_existing_username(connection, username):
    """User utility function that allows to che if a username is already taken"""
    with connection:
        cur = connection.cursor()
        res = cur.execute("SELECT COUNT(*) FROM user WHERE username=(?)", (username,)).fetchone()[0]
    return res


def check_existing_uid(connection, user_id):
    """User utility function that allows to che if a user_id exists."""
    with connection:
        cur = connection.cursor()
        res = cur.execute("SELECT COUNT(*) FROM user WHERE user_id=(?)", (user_id,)).fetchone()[0]
    return res


def get_user_and_encrypted_pw(connection, username):
    exists = check_existing_username(connection, username)
    db_password = None
    if exists:
        user_id = get_user_id(connection, username)
        db_password = get_password(connection, user_id)
    return db_password


class User:
    """User class: this class has the purpose of creating a new user Object by creating an instance of this class.
        Attributes:
                firstname: First name of the user.
                lastname: Last name of the user.
                username: Username that will be used for accessing the tool.
                password: Password that will be used for accessing the tool.
    """
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
