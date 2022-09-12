import menu
import utility

menuconnection = utility.getdbconnection('test.db')


def main():
    userid = menu.loginandregistration()

   # habitmenu(userid)


if __name__ == "__main__":
    main()
