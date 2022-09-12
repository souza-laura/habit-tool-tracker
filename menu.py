from rich.console import Console
from rich.text import Text
from cfonts import render
import questionary
import user
import utility


menuconnection = utility.getdbconnection('test.db')
console = Console()
qmark = "⭐️"
wrongpw = "☠️"

def loginandregistration():
    utility.rendertitle()
    # TODO: create menu that will be called from main
    welcomemessage = "Welcome to Habitool! Is it your first time here?"
    res = questionary.confirm(welcomemessage, qmark=qmark).ask()
    if True.__eq__(res):
        return registrationform()
    elif False.__eq__(res):
        return loginform()


def registrationform():
    registrationmessage = "Let's proceed with registration.\nWhat's your first name?"
    firstname = questionary.text(registrationmessage,
                                 validate=utility.textvalidator,
                                 qmark=qmark).ask()
    lastname = questionary.text("What's your last name?",
                                validate=utility.textvalidator,
                                qmark=qmark).ask()
    username = questionary.text("Choose a username (The username will be used for the login):",
                                validate=utility.textvalidator,
                                qmark=qmark).ask()
    exists = user.checkexistingusername(menuconnection, username)
    while exists:
        username = questionary.text("This username is already taken. Choose another one:",
                                    validate=utility.textvalidator,
                                    qmark=qmark).ask()
        exists = user.checkexistingusername(menuconnection, username)
    password = questionary.password("Choose the password: ",
                                    validate=utility.passwordvalidator,
                                    qmark=qmark).ask()
    password.encode('utf-8')
    userid = user.register(menuconnection, firstname, lastname, username.lower(), password)
    if not userid.__eq__(-1):
        text = Text("\n\nWelcome to Habitool, ")
        text.stylize("bold", 0)
        firstname = Text(firstname.lower().capitalize() + "!")
        firstname.stylize("bold orange3", 0)
        console.print(text + firstname)
        return userid
    else:
        console.print("\n\nSorry, something went wrong with your registration.😟\nTry again.\n\n", style="bold red3")
        loginandregistration()


def loginform():
    loginmessage = "Welcome back! Do you want to proceed with login?"
    wrongpasswordcounter = 0
    res = questionary.confirm(loginmessage, qmark=qmark).ask()
    if True.__eq__(res):
        username = questionary.text("Username: ", qmark=qmark).ask()
        exists = user.checkexistingusername(menuconnection, username.lower())
        while not exists:
            proceed = questionary.confirm("There's no such username. Do you want to proceed with registration?",
                                          qmark=qmark).ask()
            if True.__eq__(proceed):
                registrationform()
            username = questionary.text("Username: ", qmark=qmark).ask()
            exists = user.checkexistingusername(menuconnection, username.lower())
        password = questionary.password("Password: ", qmark=qmark).ask()
        check = user.login(menuconnection, username, password)
        while check.__eq__(-1):
            wrongpasswordcounter += 1
            password = questionary.password("Wrong password. Try again:  ", qmark=wrongpw).ask()
            check = user.login(menuconnection, username, password)
            if not check.__eq__(-1):
                break
            if wrongpasswordcounter.__eq__(3):
                pass
        text = Text("\nWelcome back to Habitool, ")
        text.stylize("bold", 0)
        firstname = Text(user.getfirstname(menuconnection, check).lower().capitalize() + "!")
        firstname.stylize("bold dark_orange", 0)
        console.print(text + firstname)
        return check
    elif False.__eq__(res):
        loginandregistration()


def showtitle():
    title = render('Habitool', gradient=['red', 'blue'])
    print(title)
