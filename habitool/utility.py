import datetime
import re

import emoji
from cfonts import render
from rich.console import Console
from rich.table import Table

from database import initialize_database

party_popper = emoji.emojize(":party_popper:")


def show_habits_table(habits: list):
    """ Utility function for showing habits' table """

    table = Table(title="User Habits", style="bold")
    table.add_column("Habit ID")
    table.add_column("Habit Name")
    table.add_column("Habit Description")
    table.add_column("Creation Date")
    table.add_column("Periodicity")
    table.add_column("Active")
    if habits:
        for hab in habits:
            date = datetime.datetime.strptime(hab[3], "%Y-%m-%d").strftime('%d/%m/%Y')
            table.add_row(str(hab[0]), hab[1], hab[2], date, hab[4], active(hab[5]))
        console = Console()
        console.print(table)
    else:
        pass
        # TODO: message that shows that user has no habits


def show_habits_progress(habits: list):
    """ Utility function for showing habits' progress """

    table = Table(title="Progress", style="bold")
    table.add_column("Habit ID")
    table.add_column("Habit Name")
    table.add_column("Habit Description")
    table.add_column("Creation Date")
    table.add_column("Completion Date")
    if habits:
        for hab in habits:
            creation_date = datetime.datetime.strptime(hab[3], "%Y-%m-%d").strftime('%d/%m/%Y')
            completion_date = datetime.datetime.strptime(hab[4], "%Y-%m-%d").strftime('%d/%m/%Y')
            table.add_row(str(hab[0]), hab[1], hab[2], creation_date, completion_date)
        console = Console()
        console.print(table)


def show_predefined_habits(habits: list):
    """ Utility function for showing predefined habits """

    table = Table(title="Predefined Habits", style="bold")
    table.add_column("Habit Name")
    table.add_column("Habit Description")
    table.add_column("Periodicity")
    for hab in habits:
        table.add_row(hab[0], hab[1], hab[2])
    console = Console()
    console.print(table)


def show_dates_streak(habits):
    """ Utility function for showing the days in a streak in which the habit was completed
     and the total of days."""
    table = Table()
    table.add_column("Date of completion", justify="center")
    for x in habits:
        date = datetime.datetime.strptime(str(x), "%Y-%m-%d").strftime('%d/%m/%Y')
        table.add_row(date)
    total = Table()
    total.add_column("Total Streak", justify="center", style="orange3")
    total.add_row(party_popper + " " + str(len(habits)) + " " + party_popper)
    console = Console()
    console.print(table, total)


def active(status: int):
    """ Utility function for showing status icon in table """

    if 0 == status:
        return emoji.emojize(":red_circle:")
    else:
        return emoji.emojize(":green_circle:")


def password_validator(password):
    """ Utility function for validating the password """
    if len(password) < 6:
        return "Password must be at least 6 characters"
    elif re.search(r'\d', password) is None:
        return "Password must contain a number"
    elif re.search("[a-z]", password) is None:
        return "Password must contain an lower-case letter"
    elif re.search("[A-Z]", password) is None:
        return "Password must contain an upper-case letter"
    else:
        return True


def text_validator(text):
    """ Utility function for validating text """
    if len(text) <= 0:
        return "Please enter a value"
    else:
        return True


def render_title():
    """ Utility function for rendering the title """
    title = render('Habitool', font='block')
    print(title)


def get_connection(dbname):
    """ Utility function for getting the connection from the database module"""
    return initialize_database(dbname)
