import sqlite3


# TODO: write documentation

def connect(database=None):
    connection = sqlite3.connect(database)
    return connection


def initializedatabase(database):
    connection = connect(database)
    cur = connection.cursor()
    exists = cur.execute("""SELECT count(*)
                            FROM sqlite_master
                            WHERE type='table' 
                            AND name='predefined_habit';""").fetchone()[0]
    # TODO: implement basic logging messages
    if not exists:
        with connection:
            with open('dbinitialization.txt') as initializer:
                for command in initializer:
                    cur.execute(command)
            initializer.close()
        # TODO: implement basic logging messages
    return connection
