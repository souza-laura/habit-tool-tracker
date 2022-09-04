import bcrypt


# TODO: DESCRIBE ALL FUNCTIONS
def register(connection, firstname, lastname, username, password):
    newuser = User()
    newuser.firstname = firstname
    newuser.lastname = lastname
    newuser.username = username
    newuser.password = bcrypt.hashpw(password, bcrypt.gensalt())
    return newuser.createuser(connection)


def login(connection, username, password):
    userdbpassword = getuserandcryptedpw(connection, username)
    if bcrypt.checkpw(password, userdbpassword):
        return _getuserid(connection, username)
    else:
        return -1


def changeusername(connection, username):
    pass


def changepassword(connection, oldpassword, newpassword):
    pass


def deleteaccount(connection, username, password):
    pass


def _getpassword(connection, userid):
    with connection:
        cur = connection.cursor()
        res = cur.execute("SELECT password FROM user WHERE user_id=(?)", (userid,)).fetchone()[0]
    return res


def _getuserid(connection, username):
    with connection:
        cur = connection.cursor()
        uid = cur.execute("SELECT user_id FROM user WHERE username=(?)", (username.lower(),)).fetchone()[0]
    return uid


def _checkexisting(connection, username):
    with connection:
        cur = connection.cursor()
        res = cur.execute("SELECT COUNT(*) FROM user WHERE username=(?)", (username,)).fetchone()[0]
    return res


def getuserandcryptedpw(connection, username):
    exists = _checkexisting(connection, username)
    if exists:
        userid = _getuserid(connection, username)
        dbpassword = _getpassword(connection, userid)
    return dbpassword


# TODO: WRITE DOCUMENTATION OF USER CLASS
class User:

    def __int__(self, firstname, lastname, username, password):
        self.firstname = firstname
        self.lastname = lastname
        self.username = username
        self.password = password

    def createuser(self, connection):
        exists = _checkexisting(connection, self.username)
        print(exists)
        if not exists:
            with connection:
                cur = connection.cursor()
                cur.execute("INSERT INTO user(first_name, last_name, username, password) VALUES (?,?,?,?)",
                            (self.firstname, self.lastname, self.username, self.password))
            return cur.lastrowid
        else:
            return -1

    def deleteuser(self, connection):
        exists = _checkexisting(connection, self.username)
        if exists:
            userid = _getuserid(connection, self.username)
            with connection:
                cur = connection.cursor()
                cur.execute("DELETE FROM user WHERE user_id=(?)", (userid,))
                rowcount = cur.rowcount
                if rowcount:
                    return rowcount
        else:
            return -1