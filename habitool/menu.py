from datetime import datetime

import questionary
from rich.console import Console
from rich.text import Text
import numpy as np

import habit
import user
import utility

# DB Initialization
menuconnection = utility.get_connection('test.db')
console = Console()

# Different QMarks for Questionary questions
qmark = "⭐️"
wrongpw = "☠️"
habitcreation = "🌱"
habitdeletion = "🔥"
habitmodification = "🔧️"
markascompl = "📗"
programexit = "📤"

# Lists that may be used more than once in the program
periodicitychoices = ["DAILY", "WEEKLY", "MONTHLY", "YEARLY"]
modificationchoices = ["Name", "Description", "Periodicity"]


def menu():
    """ Menu function that is accessed from main.py
        This is the first access to the program, from here we can login or register."""

    utility.render_title()
    welcomemessage = "Welcome to Habitool! Is it your first time here?"
    res = questionary.confirm(welcomemessage, qmark=qmark).ask()
    if True.__eq__(res):
        registration_form()
    elif False.__eq__(res):
        login_form()


def registration_form():
    """ Registration form that, as the name suggests, allows to register a new profile. We can create an account in
        order to be able to access later all program's functionalities."""
    registrationmessage = "Let's proceed with registration.\nWhat's your first name?"
    firstname = questionary.text(registrationmessage,
                                 validate=utility.text_validator,
                                 qmark=qmark).ask()
    lastname = questionary.text("What's your last name?",
                                validate=utility.text_validator,
                                qmark=qmark).ask()
    username = questionary.text("Choose a username (The username will be used for the login):",
                                validate=utility.text_validator,
                                qmark=qmark).ask()
    exists = user.check_existing_username(menuconnection, username)
    while exists:
        username = questionary.text("This username is already taken. Choose another one:",
                                    validate=utility.text_validator,
                                    qmark=qmark).ask()
        exists = user.check_existing_username(menuconnection, username)
    password = questionary.password("Choose the password: ",
                                    validate=utility.password_validator,
                                    qmark=qmark).ask()
    password.encode('utf-8')
    userid = user.register(menuconnection, firstname, lastname, username.lower(), password)
    if not userid.__eq__(-1):
        text = Text("\n\nWelcome to Habitool, ")
        text.stylize("bold", 0)
        firstname = Text(firstname.lower().capitalize() + "!")
        firstname.stylize("bold orange3")
        console.print(text + firstname)
        hashabit = habit.has_habits(menuconnection, userid)
        habit_menu(userid, hashabit)
    else:
        console.print("\n\nSorry, something went wrong with your registration.😟\nTry again.\n\n", style="bold red3")
        menu()


def login_form():
    """ Login form. This is the part of the menu that allows us to login, after registration. """
    loginmessage = Text("\nLogin 📥\n")
    loginmessage.stylize("bold light_slate_blue")
    console.print(loginmessage)
    wrongpasswordcounter = 0
    username = questionary.text("Username: ", qmark=qmark).ask()
    exists = user.check_existing_username(menuconnection, username.lower())
    while not exists:
        proceed = questionary.confirm("There's no such username. Do you want to proceed with registration?",
                                      qmark=qmark).ask()
        if True.__eq__(proceed):
            registration_form()
            break
        username = questionary.text("Username: ", qmark=qmark).ask()
        exists = user.check_existing_username(menuconnection, username.lower())
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
    firstname = Text(user.get_firstname(menuconnection, check).lower().capitalize() + "!\n")
    firstname.stylize("bold orange3", 0)
    console.print(text + firstname)
    hashabit = habit.has_habits(menuconnection, check)
    habit_menu(check, hashabit)


def first_login(userid):
    """ This is the function that is called at the user'd first login. Here we can choose whether
        we want predefined habits or not."""
    res = questionary.confirm("You don't have any habit yet. Do you want to chose some predefined habits?",
                              qmark=qmark).ask()
    if True.__eq__(res):
        choose_predefined_habits(userid)
    else:
        habit_menu(userid, 0)


def habit_menu(userid, hashabit=0):
    """ Function that allows to access the program main functionalities."""
    habitmenuchoices = ["Create a new habit",
                        "Modify an existing habit",
                        "Mark habit as completed",
                        "Activate/Deactivate habit",
                        "Delete a habit",
                        "Habits Analysis",
                        "Account Settings",
                        "Exit Habitool"]
    options = {"Create a new habit": create_new_habit,
               "Modify an existing habit": modify_habit,
               "Mark habit as completed": mark_as_completed,
               "Activate/Deactivate habit": activate_deactivate,
               "Delete a habit": delete_habit,
               "Habits Analysis": habits_analysis,
               "Account Settings": account_settings,
               "Exit Habitool": exit_program}
    if hashabit.__eq__(-1):
        first_login(userid)
    else:
        answer = questionary.select("What would you like to do?", choices=habitmenuchoices, qmark=qmark).ask()
        options[answer](userid)


def create_new_habit(userid):
    """ Function created in order to allow the creation a new habits """
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
    habitid = habit.add_new_habit(menuconnection, userid, name, description, period, active)
    exists = habit.habit_exists(menuconnection, habitid)
    if exists.__eq__(1):
        text = Text("\nNew habit successfully created!🦋\n")
        text.stylize("bold sky_blue1")
        console.print(text)
        habit_menu(userid)
    else:
        text = Text("\nSorry something went wrong. Try again.😟\n")
        text.stylize("bold red3")
        console.print(text)
        habit_menu(userid, 0)


def delete_habit(userid):
    """ Function created in order to allow the deletion of habits """
    text = Text("\nWhich habit do you want to delete? 🔥\n")
    text.stylize("bold deep_pink2")
    console.print(text)
    cont = 1
    habits = habit.get_user_habits(menuconnection, userid)
    if type(habits) == list:
        utility.show_habits_table(list(habits))
        choices = []
        for hab in habits:
            choices.append(f"{hab[0]} - {hab[1]} - {hab[4]}")
        while cont:
            answer = questionary.select("Choose the habit to delete:", qmark=habitdeletion, choices=choices).ask()
            ans = answer.split(" - ")
            confirmation = questionary.confirm("Are you sure you want to delete the habit?", qmark=habitdeletion).ask()
            if True.__eq__(confirmation):
                deleted = habit.delete_habit(menuconnection, ans[0])
                if deleted:
                    text = Text("\nThe habit was correctly deleted.🔥\n")
                    text.stylize("bold deep_pink2")
                    console.print(text)
                    proceed = questionary.confirm("Do you want to delete another habit?", qmark=habitdeletion).ask()
                    if True.__eq__(proceed):
                        cont = 1
                    else:
                        cont = 0
                else:
                    text = Text("\nSomething went wrong with habit deletion. Try again.😟\n")
                    text.stylize("bold red3")
                    console.print(text)
    habit_menu(userid)


def modify_habit(userid):
    """ Function created in order to allow the modification of habits. """
    result = 0
    text = Text("\nWhich habit do you want to modify?🔧\n")
    text.stylize("bold light_coral")
    console.print(text)
    cont = 1
    habits = habit.get_user_habits(menuconnection, userid)
    if type(habits) == list:
        utility.show_habits_table(list(habits))
        choices = []
        for hab in habits:
            choices.append(f"{hab[0]} - {hab[1]} - {hab[4]}")
        while cont:
            answer = questionary.select("Choose the habit to modify:", qmark=habitmodification, choices=choices).ask()
            ans = answer.split(" - ")
            choice = questionary.select("What do you want to modify?", choices=modificationchoices,
                                        qmark=habitmodification).ask()
            if "Name".__eq__(choice):
                result = change_habit_name(ans[0])
            if "Description".__eq__(choice):
                result = change_habit_description(ans[0])
            if "Periodicity".__eq__(choice):
                result = change_habit_periodicity(ans[0])
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
                text = Text("\nSomething went wrong with habit deletion. Try again.😟\n")
                text.stylize("bold red3")
                console.print(text)
    habit_menu(userid)


def choose_predefined_habits(userid):
    """ Function created in order to allow the choice if predefined habits (available only at the first login
        or when user do not have any habits)"""
    predef = habit.get_predefined_habits(menuconnection)
    utility.show_predefined_habits(predef)
    choices = ["I don't want any predefined habit", "1", "2", "3", "4", "5", "All of the above"]
    answer = questionary.checkbox("Select habits: ", choices=choices, qmark=qmark).ask()
    # TODO: find better and more dynamic way to add predefined habits bases on user choice
    if "All of the above" in answer:
        for p in predef:
            habit.add_predefined_habit(menuconnection, userid, p)
        answer = []
    if "I don't want any predefined habit" in answer or not answer:
        habit_menu(userid)
    if "1" in answer:
        habit.add_predefined_habit(menuconnection, userid, predef[0])
    if "2" in answer:
        habit.add_predefined_habit(menuconnection, userid, predef[1])
    if "3" in answer:
        habit.add_predefined_habit(menuconnection, userid, predef[2])
    if "4" in answer:
        habit.add_predefined_habit(menuconnection, userid, predef[3])
    if "5" in answer:
        habit.add_predefined_habit(menuconnection, userid, predef[4])
    habit_menu(userid)


def mark_as_completed(userid):
    """ Function created in order to mark habits as completed """
    text = Text("\nWhich habit do you want to mark as completed?📗\n")
    text.stylize("bold chartreuse2")
    console.print(text)
    cont = 1
    date = datetime.today().strftime('%Y-%m-%d')
    habits = habit.get_active_user_habits(menuconnection, userid)
    if type(habits) == list:
        utility.show_habits_table(list(habits))
        choices = []
        if habits:
            for hab in habits:
                choices.append(f"{hab[0]} - {hab[1]} - {hab[4]}")
            while cont:
                answer = questionary.select("Choose the habit to complete:", qmark=markascompl, choices=choices).ask()
                ans = answer.split(" - ")
                alreadycompleted = habit.check_if_already_completed(menuconnection, ans[0], date)
                if alreadycompleted.__eq__(1):
                    text = Text("\nThis habit was already completed today! Choose another one!📗")
                    text.stylize("bold chartreuse2")
                    console.print(text)
                    choices.remove(f"{ans[0]} - {ans[1]} - {ans[2]}")
                    cont = 1
                else:
                    habit.mark_habit_as_completed(menuconnection, ans[0])
                    text = Text("\nThis habit was correctly completed! Well done!🎉\n")
                    text.stylize("bold violet")
                    console.print(text)
                    proceed = questionary.confirm("Do you want to complete another habit?",
                                                  qmark=habitmodification).ask()
                    if True.__eq__(proceed):
                        cont = 1
                    else:
                        cont = 0
        else:
            text = Text("\nYou don't have any habits yet! Create new habits in order to complete them!\n")
            text.stylize("bold red3")
            console.print(text)
    habit_menu(userid)


def activate_deactivate(userid):
    """ Function created in order to allow to activate or deactivate habits """
    text = Text("\nWhich habit do you want to activate/deactivate?\n")
    text.stylize("bold chartreuse2")
    console.print(text)
    habits = habit.get_user_habits(menuconnection, userid)
    choices = []
    if type(habits) == list:
        utility.show_habits_table(list(habits))
        for hab in habits:
            choices.append(f"{hab[0]} - {hab[1]} - {hab[4]}")
        answer = questionary.select("Choose the habit to activate/deactivate:", qmark=markascompl,
                                    choices=choices).ask()
        ans = answer.split(" - ")
        habit.activate_deactivate_habit(menuconnection, ans[0])
        text = Text("\nThe activation status was changed!\n")
        text.stylize("bold deep_pink2")
        console.print(text)

    else:
        text = Text("\nYou don't have any habits yet! Create new habits in order to activate/deactivate them!\n")
        text.stylize("bold red3")
        console.print(text)
    habit_menu(userid)


def account_settings(userid):
    """ Secondary menu that allows to change username/password and delete account. """
    habitmenuchoices = ["Change Username",
                        "Change Password",
                        "Delete Account",
                        "Go back"]
    options = {"Change Username": change_username,
               "Change Password": change_password,
               "Delete Account": delete_account,
               "Go back": habit_menu}
    answer = questionary.select("What would you like to do?", choices=habitmenuchoices, qmark=habitmodification).ask()
    options[answer](userid)


def habits_analysis(userid):
    """ Secondary menu created for habits analysis. """
    habitmenuchoices = ["Show all habits",
                        "Show all active habits",
                        "Show all non-active habits",
                        "Show daily habits",
                        "Show weekly habits",
                        "Show monthly habits",
                        "Show habit's progress",
                        "Go back to main menu"]
    options = {"Show all habits": show_all,
               "Show all active habits": show_filtered_habits,
               "Show all non-active habits": show_filtered_habits,
               "Show daily habits": show_filtered_habits,
               "Show weekly habits": show_filtered_habits,
               "Show monthly habits": show_filtered_habits,
               "Show habit's progress": show_streak,
               "Go back to main menu": habit_menu
               }
    answer = questionary.select("What would you like to do?", choices=habitmenuchoices, qmark=habitmodification).ask()
    if "Show daily habits".__eq__(answer):
        options[answer](userid, "DAILY")
    elif "Show weekly habits".__eq__(answer):
        options[answer](userid, "WEEKLY")
    elif "Show monthly habits".__eq__(answer):
        options[answer](userid, "MONTHLY")
    elif "Show all active habits".__eq__(answer):
        options[answer](userid, 1, "active")
    elif "Show all non-active habits".__eq__(answer):
        options[answer](userid, 0, "active")
    else:
        options[answer](userid)


def exit_program(userid):
    """ Function of the menu that "logs out" the user (quit the program) """

    logout = questionary.confirm("Are you sure you want to exit Habitool?", qmark=programexit).ask()
    name = Text(user.get_firstname(menuconnection, userid).lower().capitalize() + "!⭐ \n")
    name.stylize("bold orange3")
    if True.__eq__(logout):
        text = Text("\nThanks for staying with us! See you soon ")
        text.stylize("bold royal_blue1")
        console.print(text + name)
        quit()
    else:
        habit_menu(userid)


def show_all(userid):
    """
    This function shows the table of all user habits (both active and non-active)
    :param userid:
    :return: none - it shows the table of all user habits
    """
    text = Text("\nThese are all your habits!")
    text.stylize("bold royal_blue1")
    habits = habit.get_user_habits(menuconnection, userid)
    if type(habits) == list:
        utility.show_habits_table(list(habits))
        habits_analysis(userid)
    else:
        text = Text("\nYou don't have any habits yet! Create new habits!\n")
        text.stylize("bold red3")
        console.print(text)


def show_streak(userid):
    """ Function created in order to calculate and show the max streak of days in which a habit was completed
        (only available for daily and active habits)."""
    connection = utility.get_connection('test.db')
    text = Text("\nFor which habit do you want to check the streak (currently available for daily habits)?\n")
    text.stylize("bold chartreuse2")
    console.print(text)
    habits = habit.get_user_habits_for_streak(connection, userid)
    choices = []
    hab = []
    if not len(habits).__eq__(0):
        utility.show_habits_table(list(habits))
        for hab in habits:
            choices.append(f"{hab[0]} - {hab[1]} - {hab[4]}")
        answer = questionary.select("Choose the habit:", qmark=markascompl,
                                    choices=choices).ask()
        ans = answer.split(" - ")
        dates = habit.get_streak(connection, ans[0])
        print(dates)
        print(type(dates))
        if type(dates) == list and len(dates) > 1:
            # calculating max streak
            npdates = np.array(dates, dtype='datetime64[D]')
            i0max, i1max = 0, 0
            i0 = 0
            for i1, date in enumerate(npdates):
                if date - npdates[i0] != np.timedelta64(i1 - i0, 'D'):
                    if i1 - i0 > i1max - i0max:
                        i0max, i1max = i0, i1
                    i0 = i1
            utility.show_dates_streak(npdates[i0max:i1max])
            message = f"\nThe maximum completion streak for this habit is: {npdates[i0max:i1max].size} days! Well done!🎉\n"
            text = Text(message)
            text.stylize("bold orange1")
            console.print(text)
        elif type(dates) == str or len(dates).__eq__(1):
            message = f"\nNo max streak available for this habit! You completed the habit once, keep completing the habit daily to keep the streak up to date!\n"
            text = Text(message)
            text.stylize("bold red3")
            console.print(text)
        else:
            message = f"\nNo streak available for this habit! Complete the habit daily to keep the streak up to date!\n"
            text = Text(message)
            text.stylize("bold red3")
            console.print(text)
    habit_menu(userid)


def show_filtered_habits(userid, filterval, column='periodicity'):
    """ Function created in order to show filtered habits (active, non-active, DAILY, WEEKLY, MONTHLY)"""
    if column.__eq__('periodicity'):
        val = filterval.lower()
        filterval = f"'{filterval}'"
    elif column.__eq__('active') and filterval.__eq__(1):
        val = 'active'
    elif column.__eq__('active') and filterval.__eq__(0):
        val = 'non-active'
    habits = habit.get_filtered_habits(menuconnection, userid, filterval, column)
    if type(habits) == list:
        message = "\nThese are all your " + f"{val}" + " habits: \n"
        text = Text(message)
        text.stylize("bold royal_blue1")
        console.print(text)
        utility.show_habits_table(list(habits))
        habits_analysis(userid)
    elif habits.__eq__(-1):
        message = "\nYou don't have any " + f"{val}" + " habits! Create a new one! \n"
        text = Text(message)
        text.stylize("bold red3")
        console.print(text)
    habit_menu(userid)


def change_habit_name(habitid):
    name = questionary.text("Choose a new name for your habit: ", qmark=habitmodification).ask()
    return habit.modify_habit(menuconnection, habitid, "habit_name", name)


def change_habit_description(habitid):
    description = questionary.text("Write a new description for your habit: ", qmark=habitmodification).ask()
    return habit.modify_habit(menuconnection, habitid, "habit_description", description)


def change_habit_periodicity(habitid):
    period = questionary.select("Chose a new description for your habit: ", choices=periodicitychoices,
                                qmark=habitmodification).ask()
    return habit.modify_habit(menuconnection, habitid, "periodicity", period)


def change_username(userid):
    """ Function created in order to allow the modification of the username """
    cont = 1
    while cont:
        username = questionary.text("Choose your new username: ", qmark=habitmodification).ask()
        password = questionary.password("Insert your password: ", qmark=habitmodification).ask()
        result = user.change_username(menuconnection, userid, username, password)
        if result.__eq__(-1):
            password = questionary.password("Wrong password. Try again: ", qmark=habitmodification).ask()
            result = user.change_username(menuconnection, userid, username, password)
        if result.__eq__(-2):
            username = questionary.text("This username is already taken. Choose a new one: ",
                                        qmark=habitmodification).ask()
            result = user.change_username(menuconnection, userid, username, password)
        if result.__eq__(1):
            text = Text("\nThe username was correctly changed! Your new username is " + username + "!🛠️\n")
            text.stylize("bold medium_purple1")
            console.print(text)
            cont = 0
    habit_menu(userid)


def change_password(userid):
    """ Function created in order to allow the modification of the password """

    cont = 1
    while cont:
        currentpassword = questionary.password("Insert your current password: ", qmark=habitmodification).ask()
        newpassword = questionary.password("Insert your new password: ", qmark=habitmodification,
                                           validate=utility.password_validator).ask()
        result = user.change_password(menuconnection, userid, currentpassword, newpassword)
        if result.__eq__(-1):
            currentpassword = questionary.password("Your current password is wrong. Try again: ",
                                                   qmark=habitmodification).ask()
            newpassword = questionary.password("Insert your new password: ", qmark=habitmodification,
                                               validate=utility.password_validator).ask()
            result = user.change_username(menuconnection, userid, currentpassword, newpassword)
        if result.__eq__(1):
            cont = 0
    text = Text("\nYour password was correctly changed!🛠️\n")
    text.stylize("bold medium_purple1")
    console.print(text)
    habit_menu(userid)


def delete_account(userid):
    """ Function created in order to allow account deletion """

    delete = questionary.confirm("Are you sure you want to delete your Habitool account?", qmark="❌").ask()
    name = Text(user.get_firstname(menuconnection, userid).lower().capitalize() + "!⭐ \n")
    name.stylize("bold orange3")
    if True.__eq__(delete):
        user.delete_account(menuconnection, userid)
        text = Text("\nWe're sorry to hear that. Thanks for staying with us. Bye,  ")
        text.stylize("bold royal_blue1")
        console.print(text + name)
        quit()
    else:
        habit_menu(userid)
