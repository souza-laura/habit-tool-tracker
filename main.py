from database import initializedatabase
import pyfiglet
from quo import echo
import user


def menu():
    # TODO: create menu that will be called from main
    pass


def main():
    connection = initializedatabase('test.db')
    welcome = pyfiglet.figlet_format("Habitool", font="ogre")
    echo(welcome, fg="red", bold=True)

    # TODO: encode password before passing to register and login

    # TODO: transform username in lowercase before passing to register and login

    # user.register(connection, "test", "laura", "lauratest", "password".encode('utf-8'))
    print(user.login(connection, "lauratest", "password".encode('utf-8')))


if __name__ == "__main__":
    main()
