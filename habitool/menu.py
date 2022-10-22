from datetime import datetime

import emoji
import questionary
from rich.console import Console
from rich.text import Text

import habit
import user
import utility

# database initialization
db_name = 'habitool.db'
menu_connection = utility.get_connection(db_name)

# EMOJIS
qmark = emoji.emojize(" :star: ")
x_emoji = emoji.emojize(" :police_car_light: ")
seedling = emoji.emojize(" :seedling: ")
fire = emoji.emojize(" :fire: ")
wrench = emoji.emojize(" :wrench: ")
green_book = emoji.emojize(" :green_book: ")
outbox_tray = emoji.emojize(" :outbox_tray: ")
inbox_tray = emoji.emojize(" :inbox_tray: ")
confused_emoji = emoji.emojize(" :confused: ")
butterfly = emoji.emojize(" :butterfly: ")
party_popper = emoji.emojize(" :party_popper: ")
balloon = emoji.emojize(" :balloon: ")
hammer_and_wrench = emoji.emojize(" :hammer_and_wrench: ")

# Lists that may be used more than once in the program
periodicity_choices = ["DAILY", "WEEKLY", "MONTHLY", "YEARLY"]
modification_choices = ["Name", "Description", "Periodicity"]

# rich console
console = Console()


def menu():
    """ Menu function that is accessed from main.py
        This is the first access to the program, from here we can login or register."""
    # rendering the title
    utility.render_title()
    welcome_message = "Welcome to Habitool! Is it your first time here?"
    res = questionary.confirm(welcome_message, qmark=qmark).ask()
    if True.__eq__(res):
        registration_form()
    elif False.__eq__(res):
        login_form()


def registration_form():
    """ Registration form that, as the name suggests, allows to register a new profile. We can create an account in
        order to be able to access later all program's functionalities."""
    registration_message = "Let's proceed with registration.\nWhat's your first name?"
    firstname = questionary.text(registration_message,
                                 validate=utility.text_validator,
                                 qmark=qmark).ask()
    lastname = questionary.text("What's your last name?",
                                validate=utility.text_validator,
                                qmark=qmark).ask()
    username = questionary.text("Choose a username (The username will be used for the login):",
                                validate=utility.text_validator,
                                qmark=qmark).ask()
    # check if the inserted username already exists
    exists = user.check_existing_username(menu_connection, username)
    while exists:
        username = questionary.text("This username is already taken. Choose another one:",
                                    validate=utility.text_validator,
                                    qmark=qmark).ask()
        # check again
        exists = user.check_existing_username(menu_connection, username)
    password = questionary.password("Choose the password: ",
                                    validate=utility.password_validator,
                                    qmark=qmark).ask()
    # encode password before encrypting
    password.encode('utf-8')
    # registration that returns the user id that belongs to the newly registered user
    user_id = user.register(menu_connection, firstname, lastname, username.lower(), password)
    if not user_id.__eq__(-1):
        text = Text("\n\nWelcome to Habitool, ")
        text.stylize("bold", 0)
        firstname = Text(firstname.lower().capitalize() + "!")
        firstname.stylize("bold orange3")
        console.print(text + firstname)
        hashabit = habit.has_habits(menu_connection, user_id)
        habit_menu(user_id, hashabit)
    else:
        console.print(f"\n\nSorry, something went wrong with your registration.{confused_emoji}\nTry again.\n\n",
                      style="bold red3")
        menu()


def login_form():
    """ Login form. This is the part of the menu that allows us to login, after registration. """
    login_message = Text(f"\nLogin {inbox_tray}\n")
    login_message.stylize("bold light_slate_blue")
    console.print(login_message)
    wrong_password_counter = 0
    username = questionary.text("Username: ", qmark=qmark).ask()
    exists = user.check_existing_username(menu_connection, username.lower())
    # che if the account actually exists
    while not exists:
        # new registration if it doesn't exist
        proceed = questionary.confirm("There's no such username. Do you want to proceed with registration?",
                                      qmark=qmark).ask()
        if True.__eq__(proceed):
            registration_form()
            break
        username = questionary.text("Username: ", qmark=qmark).ask()
        exists = user.check_existing_username(menu_connection, username.lower())
    password = questionary.password("Password: ", qmark=qmark).ask()
    check = user.login(menu_connection, username.lower(), password)
    while check.__eq__(-1):
        wrong_password_counter += 1
        password = questionary.password("Wrong password. Try again:  ", qmark=x_emoji).ask()
        check = user.login(menu_connection, username, password)
        if not check.__eq__(-1):
            break
        if wrong_password_counter.__eq__(3):
            text = Text(
                f"\nYou digited the wrong password too many times. Try again, or re-register!{confused_emoji}\n")
            text.stylize("bold red3")
            console.print(text)
            login_form()
    # Personalized login message
    text = Text("\nWelcome back to Habitool, ")
    text.stylize("bold", 0)
    firstname = Text(user.get_firstname(menu_connection, check).lower().capitalize() + "!\n")
    firstname.stylize("bold orange3", 0)
    console.print(text + firstname)
    # everytime i check if the user has habits
    has_habit = habit.has_habits(menu_connection, check)
    habit_menu(check, has_habit)


def first_login(user_id):
    """ This is the function that is called at the user's first login. Here we can choose whether
        we want predefined habits or not."""
    response = questionary.confirm("You don't have any habit yet. Do you want to chose some predefined habits?",
                                   qmark=qmark).ask()
    if True.__eq__(response):
        choose_predefined_habits(user_id)
    else:
        habit_menu(user_id, 0)


def habit_menu(user_id, has_habit=0):
    """ Function that allows to access the program main functionalities."""
    habit_menu_choices = ["Create a new habit",
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
    if has_habit.__eq__(-1):
        # if it doesn't has habits, choose if want predefined habits
        first_login(user_id)
    else:
        answer = questionary.select("What would you like to do?", choices=habit_menu_choices, qmark=qmark).ask()
        options[answer](user_id)


def create_new_habit(user_id):
    """ Function created in order to allow the creation a new habits """
    text = Text(f"\nLet's create a new habit!{butterfly}\n")
    text.stylize("bold sky_blue1")
    console.print(text)
    name = questionary.text("Choose a name for your new habit: ", qmark=seedling).ask()
    description = questionary.text("Choose a description for your new habit: ", qmark=seedling).ask()
    period = questionary.select("Choose a periodicity for your new habit: ",
                                choices=periodicity_choices, qmark=seedling).ask()
    active = questionary.confirm("Do you want to activate the habit?", qmark=seedling).ask()
    if True.__eq__(active):
        active = 1
    else:
        active = 0
    # create new habit
    habit_id = habit.add_new_habit(menu_connection, user_id, name, description, period, active)
    # check if the habit was successfully created ->
    exists = habit.habit_exists(menu_connection, habit_id)
    if exists.__eq__(1):
        text = Text(f"\nNew habit successfully created!{butterfly}\n")
        text.stylize("bold sky_blue1")
        console.print(text)
        #  -> if so, got to main menu
        habit_menu(user_id)
    else:
        text = Text(f"\nSorry something went wrong. Try again.{confused_emoji}\n")
        text.stylize("bold red3")
        console.print(text)
        habit_menu(user_id, 0)


def delete_habit(user_id):
    """ Function created in order to allow the deletion of habits """
    text = Text(f"\nWhich habit do you want to delete?{fire}\n")
    text.stylize("bold deep_pink2")
    console.print(text)
    continue_flow = 1
    # get user habits
    habits = habit.get_user_habits(menu_connection, user_id)
    if type(habits) == list:
        utility.show_habits_table(list(habits))
        choices = []
        for hab in habits:
            choices.append(f"{hab[0]} - {hab[1]} - {hab[4]}")
        while continue_flow:
            answer = questionary.select("Choose the habit to delete:", qmark=fire, choices=choices).ask()
            ans = answer.split(" - ")
            confirmation = questionary.confirm("Are you sure you want to delete the habit?", qmark=fire).ask()
            if True.__eq__(confirmation):
                # delete habit by passing habit id
                deleted = habit.delete_habit(menu_connection, ans[0])
                if deleted:
                    text = Text(f"\nThe habit was correctly deleted.{fire}\n")
                    text.stylize("bold deep_pink2")
                    console.print(text)
                    proceed = questionary.confirm("Do you want to delete another habit?", qmark=fire).ask()
                    # user can proceed with other deletions
                    if True.__eq__(proceed):
                        continue_flow = 1
                    else:
                        # exit the loop
                        continue_flow = 0
                else:
                    text = Text(f"\nSomething went wrong with habit deletion. Try again.{confused_emoji}\n")
                    text.stylize("bold red3")
                    console.print(text)
    # go back to main menu
    habit_menu(user_id)


def modify_habit(user_id):
    """ Function created in order to allow the modification of habits. """
    result = 0
    text = Text(f"\nWhich habit do you want to modify?{wrench}\n")
    text.stylize("bold light_coral")
    console.print(text)
    continue_flow = 1
    # get user habits
    habits = habit.get_user_habits(menu_connection, user_id)
    if type(habits) == list:
        utility.show_habits_table(list(habits))
        choices = []
        for hab in habits:
            choices.append(f"{hab[0]} - {hab[1]} - {hab[4]}")
        while continue_flow:
            answer = questionary.select("Choose the habit to modify:", qmark=wrench, choices=choices).ask()
            ans = answer.split(" - ")
            choice = questionary.select("What do you want to modify?", choices=modification_choices,
                                        qmark=wrench).ask()
            # based on the choice, change name / description / periodicity by passing user
            if "Name".__eq__(choice):
                result = change_habit_name(ans[0])
            if "Description".__eq__(choice):
                result = change_habit_description(ans[0])
            if "Periodicity".__eq__(choice):
                result = change_habit_periodicity(ans[0])
            if result.__eq__(1):
                text = Text(f"\nThe habit was correctly modified.{wrench}\n")
                text.stylize("bold light_coral")
                console.print(text)
                proceed = questionary.confirm("Do you want to modify another habit?", qmark=wrench).ask()
                if True.__eq__(proceed):
                    continue_flow = 1
                else:
                    continue_flow = 0
            else:
                text = Text(f"\nSomething went wrong with habit deletion. Try again.{confused_emoji}\n")
                text.stylize("bold red3")
                console.print(text)
    habit_menu(user_id)


def choose_predefined_habits(user_id):
    """ Function created in order to allow the choice if predefined habits (available only at the first login
        or when user do not have any habits)"""
    predef = habit.get_predefined_habits(menu_connection)
    utility.show_predefined_habits(predef)
    choices = ["I don't want any predefined habit", "1", "2", "3", "4", "5", "All of the above"]
    answer = questionary.checkbox("Select habits: ", choices=choices, qmark=qmark).ask()
    # TODO: find better and more dynamic way to add predefined habits based on user choice
    if "All of the above" in answer:
        for p in predef:
            habit.add_predefined_habit(menu_connection, user_id, p)
        answer = []
    if "I don't want any predefined habit" in answer or not answer:
        habit_menu(user_id)
    if "1" in answer:
        habit.add_predefined_habit(menu_connection, user_id, predef[0])
    if "2" in answer:
        habit.add_predefined_habit(menu_connection, user_id, predef[1])
    if "3" in answer:
        habit.add_predefined_habit(menu_connection, user_id, predef[2])
    if "4" in answer:
        habit.add_predefined_habit(menu_connection, user_id, predef[3])
    if "5" in answer:
        habit.add_predefined_habit(menu_connection, user_id, predef[4])
    habit_menu(user_id)


def mark_as_completed(user_id):
    """ Function created in order to mark habits as completed """
    text = Text(f"\nWhich habit do you want to mark as completed?{green_book}\n")
    text.stylize("bold chartreuse2")
    console.print(text)
    continue_flow = 1
    date = datetime.today().strftime('%Y-%m-%d')
    habits = habit.get_active_user_habits(menu_connection, user_id)
    if type(habits) == list:
        utility.show_habits_table(list(habits))
        choices = []
        if habits:
            for hab in habits:
                choices.append(f"{hab[0]} - {hab[1]} - {hab[4]}")
            while continue_flow:
                answer = questionary.select("Choose the habit to complete:", qmark=green_book, choices=choices).ask()
                ans = answer.split(" - ")
                # check if habit was already marked as completed on the same day
                already_completed = habit.check_if_already_completed(menu_connection, ans[0], date)
                if already_completed.__eq__(1):
                    text = Text(f"\nThis habit was already completed today! Choose another one!{green_book}")
                    text.stylize("bold chartreuse2")
                    console.print(text)
                    # remove habit already completed from list
                    choices.remove(f"{ans[0]} - {ans[1]} - {ans[2]}")
                    continue_flow = 1
                else:
                    habit.mark_habit_as_completed(menu_connection, ans[0])
                    text = Text(f"\nThis habit was correctly completed! Well done!{party_popper}\n")
                    text.stylize("bold violet")
                    console.print(text)
                    proceed = questionary.confirm("Do you want to complete another habit?",
                                                  qmark=wrench).ask()
                    if True.__eq__(proceed):
                        continue_flow = 1
                    else:
                        continue_flow = 0
        else:
            text = Text("\nYou don't have any habits yet! Create new habits in order to complete them!\n")
            text.stylize("bold red3")
            console.print(text)
    habit_menu(user_id)


def activate_deactivate(user_id):
    """ Function created in order to allow to activate or deactivate habits """
    text = Text("\nWhich habit do you want to activate/deactivate?\n")
    text.stylize("bold chartreuse2")
    console.print(text)
    habits = habit.get_user_habits(menu_connection, user_id)
    choices = []
    if type(habits) == list:
        utility.show_habits_table(list(habits))
        for hab in habits:
            choices.append(f"{hab[0]} - {hab[1]} - {hab[4]}")
        answer = questionary.select("Choose the habit to activate/deactivate:", qmark=balloon,
                                    choices=choices).ask()
        ans = answer.split(" - ")
        habit.activate_deactivate_habit(menu_connection, ans[0])
        text = Text(f"\nThe activation status was changed!{balloon}\n")
        text.stylize("bold deep_pink2")
        console.print(text)

    else:
        text = Text("\nYou don't have any habits yet! Create new habits in order to activate/deactivate them!\n")
        text.stylize("bold red3")
        console.print(text)
    habit_menu(user_id)


def account_settings(user_id):
    """ Secondary menu that allows to change username/password and delete account. """
    account_menu_choices = ["Change Username",
                            "Change Password",
                            "Delete Account",
                            "Go back"]
    options = {"Change Username": change_username,
               "Change Password": change_password,
               "Delete Account": delete_account,
               "Go back": habit_menu}
    answer = questionary.select("What would you like to do?", choices=account_menu_choices, qmark=wrench).ask()
    options[answer](user_id)


def habits_analysis(user_id):
    """ Secondary menu created for habits analysis. """
    habit_analysis_menu_choices = ["Show all habits",
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
    answer = questionary.select("What would you like to do?", choices=habit_analysis_menu_choices, qmark=wrench).ask()
    if "Show daily habits".__eq__(answer):
        options[answer](user_id, "DAILY")
    elif "Show weekly habits".__eq__(answer):
        options[answer](user_id, "WEEKLY")
    elif "Show monthly habits".__eq__(answer):
        options[answer](user_id, "MONTHLY")
    elif "Show all active habits".__eq__(answer):
        options[answer](user_id, 1, "active")
    elif "Show all non-active habits".__eq__(answer):
        options[answer](user_id, 0, "active")
    else:
        options[answer](user_id)


def exit_program(user_id):
    """ Function of the menu that "logs out" the user (quit the program) """
    logout = questionary.confirm("Are you sure you want to exit Habitool?", qmark=outbox_tray).ask()
    name = Text(user.get_firstname(menu_connection, user_id).lower().capitalize() + f"!{qmark}\n")
    name.stylize("bold orange3")
    if True.__eq__(logout):
        text = Text("\nThanks for staying with us! See you soon ")
        text.stylize("bold light_slate_blue")
        console.print(text + name)
        quit()
    else:
        habit_menu(user_id)


def show_all(user_id):
    """ This function shows the table of all user habits (both active and non-active) """
    text = Text("\nThese are all your habits!")
    text.stylize("bold royal_blue1")
    habits = habit.get_user_habits(menu_connection, user_id)
    if type(habits) == list and habits:
        utility.show_habits_table(list(habits))
        habits_analysis(user_id)
    else:
        text = Text("\nYou don't have any habits yet! Create new habits!\n")
        text.stylize("bold red3")
        console.print(text)
        habit_menu(user_id)


def show_streak(user_id):
    """ Function created in order to calculate and show the max streak of days in which a habit was completed
        (only available for daily and active habits)."""
    connection = utility.get_connection(db_name)
    text = Text("\nFor which habit do you want to check the streak (currently available for daily habits)?\n")
    text.stylize("bold chartreuse2")
    console.print(text)
    habits = habit.get_user_habits_for_streak(connection, user_id)
    choices = []
    if not len(habits).__eq__(0):
        utility.show_habits_table(list(habits))
        for hab in habits:
            choices.append(f"{hab[0]} - {hab[1]} - {hab[4]}")
        answer = questionary.select("Choose the habit:", qmark=green_book,
                                    choices=choices).ask()
        ans = answer.split(" - ")
        dates = habit.get_streak(connection, ans[0])
        if type(dates) == list and len(dates) > 1:
            # calculating max streak using np.array
            np_dates = habit.get_habit_max_streak(dates)
            utility.show_dates_streak(np_dates)
            message = f"\nThe maximum completion streak for this habit is: {np_dates.size} days! Well done!{party_popper}\n"
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
    habit_menu(user_id)


def show_filtered_habits(user_id, filter_value, column='periodicity'):
    """ Function created in order to show filtered habits (active, non-active, DAILY, WEEKLY, MONTHLY)"""
    if column.__eq__('periodicity'):
        val = filter_value.lower()
        filter_value = f"'{filter_value}'"
    elif column.__eq__('active') and filter_value.__eq__(1):
        val = 'active'
    elif column.__eq__('active') and filter_value.__eq__(0):
        val = 'non-active'
    habits = habit.get_filtered_habits(menu_connection, user_id, filter_value, column)
    if type(habits) == list:
        message = "\nThese are all your " + f"{val}" + " habits: \n"
        text = Text(message)
        text.stylize("bold royal_blue1")
        console.print(text)
        utility.show_habits_table(list(habits))
        habits_analysis(user_id)
    elif habits.__eq__(-1):
        message = "\nYou don't have any " + f"{val}" + " habits! Create a new one! \n"
        text = Text(message)
        text.stylize("bold red3")
        console.print(text)
    habit_menu(user_id)


def change_habit_name(habit_id):
    """ Function created in order to allow the modification of a habit's name """
    name = questionary.text("Choose a new name for your habit: ", qmark=wrench).ask()
    return habit.modify_habit(menu_connection, habit_id, "habit_name", name)


def change_habit_description(habit_id):
    """ Function created in order to allow the modification of a habit's description """
    description = questionary.text("Write a new description for your habit: ", qmark=wrench).ask()
    return habit.modify_habit(menu_connection, habit_id, "habit_description", description)


def change_habit_periodicity(habit_id):
    """ Function created in order to allow the modification of a habit's periodicity """

    period = questionary.select("Chose a new description for your habit: ", choices=periodicity_choices,
                                qmark=wrench).ask()
    return habit.modify_habit(menu_connection, habit_id, "periodicity", period)


def change_username(user_id):
    """ Function created in order to allow the modification of the username """
    continue_flow = 1
    while continue_flow:
        username = questionary.text("Choose your new username: ", qmark=wrench).ask()
        password = questionary.password("Insert your password: ", qmark=wrench).ask()
        result = user.change_username(menu_connection, user_id, username, password)
        if result.__eq__(-1):
            password = questionary.password("Wrong password. Try again: ", qmark=wrench).ask()
            result = user.change_username(menu_connection, user_id, username, password)
        if result.__eq__(-2):
            username = questionary.text("This username is already taken. Choose a new one: ",
                                        qmark=wrench).ask()
            result = user.change_username(menu_connection, user_id, username, password)
        if result.__eq__(1):
            text = Text(
                "\nThe username was correctly changed! Your new username is " + username + f"!{hammer_and_wrench}\n")
            text.stylize("bold medium_purple1")
            console.print(text)
            continue_flow = 0
    habit_menu(user_id)


def change_password(user_id):
    """ Function created in order to allow the modification of the password """
    continue_flow = 1
    while continue_flow:
        current_password = questionary.password("Insert your current password: ", qmark=wrench).ask()
        new_password = questionary.password("Insert your new password: ", qmark=wrench,
                                            validate=utility.password_validator).ask()
        result = user.change_password(menu_connection, user_id, current_password, new_password)
        if result.__eq__(-1):
            current_password = questionary.password("Your current password is wrong. Try again: ",
                                                    qmark=wrench).ask()
            new_password = questionary.password("Insert your new password: ", qmark=wrench,
                                                validate=utility.password_validator).ask()
            result = user.change_username(menu_connection, user_id, current_password, new_password)
        if result.__eq__(1):
            continue_flow = 0
    text = Text(f"\nYour password was correctly changed!{hammer_and_wrench}\n")
    text.stylize("bold medium_purple1")
    console.print(text)
    habit_menu(user_id)


def delete_account(user_id):
    """ Function created in order to allow account deletion """
    delete = questionary.confirm("Are you sure you want to delete your Habitool account?", qmark=x_emoji).ask()
    name = Text(user.get_firstname(menu_connection, user_id).lower().capitalize() + f"!{qmark}\n")
    name.stylize("bold orange3")
    if True.__eq__(delete):
        user.delete_account(menu_connection, user_id)
        text = Text("\nWe're sorry to hear that. Thanks for staying with us. Bye,  ")
        text.stylize("bold light_slate_blue")
        console.print(text + name)
        quit()
    else:
        habit_menu(user_id)
