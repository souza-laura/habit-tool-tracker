from rich.table import Table
from rich.console import Console
import re
from cfonts import render
from database import initializedatabase


def showhabitstable(habits: list):
    table = Table(title="User Habits", style="bold")
    table.add_column("Habit ID")
    table.add_column("Habit Name")
    table.add_column("Habit Description")
    table.add_column("Creation Date")
    table.add_column("Periodicity")
    table.add_column("Active")
    if habits:
        for hab in habits:
            table.add_row(str(hab[0]), hab[1], hab[2], hab[3], hab[4], active(hab[5]))
        console = Console()
        console.print(table)
    else:
        pass
        # TODO: message that shows that user has no habits


def active(status: int):
    if 0 == status:
        return "🔴"
    else:
        return "🟢"


def passwordvalidator(password):
    if len(password) < 8:
        return "Password must be at least 8 characters"
    elif re.search(r'\d', password) is None:
        return "Password must contain a number"
    elif re.search("[a-z]", password) is None:
        return "Password must contain an lower-case letter"
    elif re.search("[A-Z]", password) is None:
        return "Password must contain an upper-case letter"
    else:
        return True


def textvalidator(text):
    if len(text) <= 0:
        return "Please enter a value"
    else:
        return True


def rendertitle():
    title = render('Habitool', gradient=['red', 'blue'])
    print(title)


def getdbconnection(dbname):
    return initializedatabase(dbname)