import sqlite3


# TODO: write documentation

def connect(database=None):
    """ Connect to the database passed as parameter."""
    connection = sqlite3.connect(database)
    return connection


def initialize_database(database):
    """ This utility function checks if the database is already initialized and ready to be used, if not
        it will execute all queries in the dbinitialization.txt file"""
    connection = connect(database)
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
