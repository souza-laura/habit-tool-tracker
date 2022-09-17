import questionary
from cfonts import render
from rich.console import Console
from rich.text import Text
import numpy as np
from datetime import datetime

import habit
import user
import utility

menuconnection = utility.getdbconnection('test.db')
console = Console()
qmark = "⭐️"
wrongpw = "☠️"
habitcreation = "🌱"
habitdeletion = "🔥"
habitmodification = "🔧️"
markascompl = "✅"
periodicitychoices = ["DAILY", "WEEKLY", "MONTHLY", "YEARLY"]
modificationchoices = ["Name", "Description", "Periodicity"]


def menu():
    utility.rendertitle()
    welcomemessage = "Welcome to Habitool! Is it your first time here?"
    res = questionary.confirm(welcomemessage, qmark=qmark).ask()
    if True.__eq__(res):
        registrationform()
    elif False.__eq__(res):
        loginform()


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
        hashabit = habit.hashabits(menuconnection, userid)
        habitmenu(userid, hashabit)
    else:
        console.print("\n\nSorry, something went wrong with your registration.😟\nTry again.\n\n", style="bold red3")
        menu()


def loginform():
    loginmessage = "Login."
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
                break
            username = questionary.text("\n\nUsername: ", qmark=qmark).ask()
            exists = user.checkexistingusername(menuconnection, username.lower())
        password = questionary.password("Password: ", qmark=qmark).ask()
        check = user.login(menuconnection, username.lower(), password)
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
        firstname = Text(user.getfirstname(menuconnection, check).lower().capitalize() + "!\n")
        firstname.stylize("bold orange3", 0)
        console.print(text + firstname)
        hashabit = habit.hashabits(menuconnection, check)
        habitmenu(check, hashabit)
    elif False.__eq__(res):
        menu()


def firstlogin(userid):
    res = questionary.confirm("You don't have any habit yet. Do you want to chose some predefined habits?",
                              qmark=qmark).ask()
    if True.__eq__(res):
        chosepredefinedhabits(userid)
    else:
        habitmenu(userid, 0)


def habitmenu(userid, hashabit=0):
    habitmenuchoices = ["Create a new habit",
                        "Modify an existing habit",
                        "Mark habit as completed",
                        "Delete a habit",
                        "Habits Analysis",
                        "Account Settings",
                        "Exit Habitool"]
    options = {"Create a new habit": createnewhabit,
               "Modify an existing habit": modifyhabit,
               "Mark habit as completed": markascompleted,
               "Delete a habit": deletehabit,
               "Habits Analysis": habitsanalysis,
               "Account Settings": accountsettings,
               "Exit Habitool": exitprogram}
    if hashabit.__eq__(-1):
        firstlogin(userid)
    else:
        answer = questionary.select("What would you like to do?", choices=habitmenuchoices, qmark=qmark).ask()
        options[answer](userid)


def accountsettings(userid):
    pass


def habitsanalysis(userid):
    pass


def createnewhabit(userid):
    text = Text("\n\nLet's create a new habit! 🦋\n\n")
    text.stylize("bold sky_blue1")
    console.print(text)
    name = questionary.text("Choose a name for your new habit: ", qmark=habitcreation).ask()
    description = questionary.text("Choose a description for your new habit: ", qmark=habitcreation).ask()
    period = questionary.select("Choose a periodicity for your new habit: ",
                                choices=periodicitychoices, qmark=habitcreation).ask()
    active = questionary.confirm("Do you want to activate the habit?", qmark=habitcreation).ask()
    if True.__eq__(active):
        active = 1
    else:
        active = 0
    habitid = habit.addnewhabit(menuconnection, userid, name, description, period, active)
    exists = habit.habitexists(menuconnection, habitid)
    if exists.__eq__(1):
        text = Text("\nNew habit successfully created! 🦋\n")
        text.stylize("bold sky_blue1")
        console.print(text)
        habitmenu(userid)
    else:
        text = Text("\nSorry something went wrong. Try again. 😟\n")
        text.stylize("bold red3")
        console.print(text)
        habitmenu(userid, 0)


def deletehabit(userid):
    text = Text("\nWhich habit do you want to delete? 🔥\n")
    text.stylize("bold deep_pink2")
    console.print(text)
    cont = 1
    habits = habit.getuserhabits(menuconnection, userid)
    utility.showhabitstable(list(habits))
    choices = []
    for hab in habits:
        choices.append(f"{hab[0]} - {hab[1]} - {hab[4]}")
    while cont:
        answer = questionary.select("Choose the habit to delete:", qmark=habitdeletion, choices=choices).ask()
        ans = answer.split(" - ")
        confirmation = questionary.confirm("Are you sure you want to delete the habit?", qmark=habitdeletion).ask()
        if True.__eq__(confirmation):
            deleted = habit.deletehabit(menuconnection, ans[0])
            if deleted:
                text = Text("\nThe habit was correctly deleted. 🔥\n")
                text.stylize("bold deep_pink2")
                console.print(text)
                proceed = questionary.confirm("Do you want to delete another habit?", qmark=habitdeletion).ask()
                if True.__eq__(proceed):
                    cont = 1
                else:
                    cont = 0
            else:
                text = Text("\nSomething went wrong with habit deletion. Try again. 😟\n")
                text.stylize("bold deep_pink2")
                console.print(text)
    habitmenu(userid)


def modifyhabit(userid):
    result = 0
    text = Text("\nWhich habit do you want to modify? 🔧\n")
    text.stylize("bold light_coral")
    console.print(text)
    cont = 1
    habits = habit.getuserhabits(menuconnection, userid)
    utility.showhabitstable(list(habits))
    choices = []
    for hab in habits:
        choices.append(f"{hab[0]} - {hab[1]} - {hab[4]}")

    while cont:
        answer = questionary.select("Choose the habit to modify:", qmark=habitmodification, choices=choices).ask()
        ans = answer.split(" - ")
        choice = questionary.select("What do you want to modify?", choices=modificationchoices,
                                    qmark=habitmodification).ask()
        if "Name".__eq__(choice):
            result = changehabitname(ans[0])
        if "Description".__eq__(choice):
            result = changehabitdescription(ans[0])
        if "Periodicity".__eq__(choice):
            result = changehabitperiodicity(ans[0])
        if result.__eq__(1):
            text = Text("\nThe habit was correctly modified. 🔧\n")
            text.stylize("bold light_coral")
            console.print(text)
            proceed = questionary.confirm("Do you want to modify another habit?", qmark=habitmodification).ask()
            if True.__eq__(proceed):
                cont = 1
            else:
                cont = 0
        else:
            text = Text("\nSomething went wrong with habit deletion. Try again. 😟\n")
            text.stylize("bold deep_pink2")
            console.print(text)
    habitmenu(userid)


def chosepredefinedhabits(userid):
    predef = habit.getpredefinedhabits(menuconnection)
    utility.showpredefinedhabits(predef)
    choices = ["I don't want any predefined habit", "1", "2", "3", "4", "5", "All of the above"]
    answer = questionary.checkbox("Select habits: ", choices=choices, qmark=qmark).ask()
    # TODO: find better and more dynamic way to add predefined habits bases on user choice
    if "All of the above" in answer:
        for p in predef:
            habit.addpredefinedhabit(menuconnection, userid, p)
        answer = []
    if "I don't want any predefined habit" in answer or not answer:
        habitmenu()
    if "1" in answer:
        print(predef[0])
        habit.addpredefinedhabit(menuconnection, userid, predef[0])
    if "2" in answer:
        habit.addpredefinedhabit(menuconnection, userid, predef[1])
    if "3" in answer:
        habit.addpredefinedhabit(menuconnection, userid, predef[2])
    if "4" in answer:
        habit.addpredefinedhabit(menuconnection, userid, predef[3])
    if "5" in answer:
        habit.addpredefinedhabit(menuconnection, userid, predef[4])
    habitmenu(userid)


def markascompleted(userid):
    text = Text("\nWhich habit do you want to mark as completed? ✅\n")
    text.stylize("bold chartreuse2")
    console.print(text)
    cont = 1
    date = datetime.today().strftime('%Y-%m-%d')
    habits = habit.getuserhabits(menuconnection, userid)
    utility.showhabitstable(list(habits))
    choices = []
    for hab in habits:
        choices.append(f"{hab[0]} - {hab[1]} - {hab[4]}")
    while cont:
        answer = questionary.select("Choose the habit to complete:", qmark=markascompl, choices=choices).ask()
        ans = answer.split(" - ")
        alreadycompleted = habit.checkifalreadycompleted(menuconnection, ans[0], date)
        print(alreadycompleted)
        if alreadycompleted.__eq__(1):
            text = Text("\nThis habit was already completed today! Choose another one!✅")
            text.stylize("bold chartreuse2")
            console.print(text)
            choices.remove(f"{ans[0]} - {ans[1]} - {ans[2]}")
            cont = 1
            print(choices)
        else:
            habit.markhabitascompleted(menuconnection, ans[0])
            cont = 0


def changehabitname(habitid):
    name = questionary.text("Choose a new name for your habit: ", qmark=habitmodification).ask()
    return habit.modifyhabit(menuconnection, habitid, "habit_name", name)


def changehabitdescription(habitid):
    description = questionary.text("Write a new description for your habit: ", qmark=habitmodification).ask()
    return habit.modifyhabit(menuconnection, habitid, "habit_description", description)


def changehabitperiodicity(habitid):
    period = questionary.select("Chose a new description for your habit: ", choices=periodicitychoices,
                                qmark=habitmodification).ask()
    return habit.modifyhabit(menuconnection, habitid, "periodicity", period)


def showtitle():
    title = render('Habitool', gradient=['red', 'blue'])
    print(title)


def exitprogram():
    pass
