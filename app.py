import psycopg2 as pg2
import os
import webbrowser


## Enter the 3 credentials below!!!
database_name = ''
user = ''
password = ''





connection = pg2.connect(database = database_name, user = user, password = password)
cursor = connection.cursor()

CREATE_FOLDER_TABLE = """CREATE TABLE IF NOT EXISTS folder (
folder_id SERIAL PRIMARY KEY,folder_name VARCHAR(50) UNIQUE NOT NULL);"""
CREATE_LINK_TABLE = """CREATE TABLE IF NOT EXISTS link (link_id SERIAL PRIMARY KEY,link_name VARCHAR(50) UNIQUE NOT NULL,
url VARCHAR(50) NOT NULL,folder_id INTEGER NOT NULL REFERENCES folder(folder_id));"""


with connection:
    cursor.execute(CREATE_FOLDER_TABLE)
    cursor.execute(CREATE_LINK_TABLE)

ADD_FOLDER = """INSERT INTO folder (folder_name) VALUES (%s);"""
ADD_LINK = """INSERT INTO link (link_name, url, folder_id) VALUES (%s,%s,%s);"""

def view_folders():
    with connection:
        cursor.execute("SELECT * FROM folder;")
        results = cursor.fetchall()
    if len(results) == 0:
        print("There are currently no folders.\n")
    else:
        show_folders(results)

    while True:
        print("Enter 1 to select a folder\nEnter 2 to add a folder\nEnter 3 to go to the Main Menu")
        decision = input()
        try:
            decision = int(decision)
        except:
            print("Invalid input.\n")
            continue
        if decision not in {1,2,3}:
            print("Please select a valid option.\n")
            continue
        if decision == 1:
            if len(results) == 0:
                main_menu()
            else:
                select_folder()
                break

        elif decision == 2:
            add_folder()
            break

        elif decision ==3:
            main_menu()
            break
        break

def select_folder():
    with connection:
        cursor.execute("SELECT folder_id from folder;")

        folder_possibilities =cursor.fetchall()

    while True:


        folder_choice = input("Enter the Folder ID of the folder you would like to select:\n")

        try:
            folder_choice = int(folder_choice)


        except:

            print("Invalid input.\n")
            continue

        with connection:
            cursor.execute("SELECT * FROM folder WHERE folder_id = %s;",(folder_choice,))
            result = cursor.fetchall()

        if not result:
            print("There is no folder with that ID.\n")
            continue
        else:
            load_folder(result)
            break

def load_folder(result):
    print(result)
    print(f"Folder ID: {result[0][0]}",end="          ")
    print(f"Folder Name: {result[0][1]}")
    print("\n")
    with connection:
        cursor.execute("""SELECT link_name,url FROM link JOIN folder on link.folder_id = folder.folder_id WHERE folder.folder_id = %s;""",(result[0][0],))
        results = cursor.fetchall()

    if len(results) == 0:
        print("There are currently no links in the Group.\n")
    else:
        for x in results:
            print(x[0],end="           ")
            print(x[1])
            print()

    while True:
        decision = input("Enter 1 to launch the links\nEnter 2 to add a link the the Group\nEnter 3 to go to the Main Menu\n")

        try:
            decision = int(decision)
        except:
            print("Invalid input.\n")
        if decision not in {1,2,3}:
            print("Please select a valid option.\n")
            continue

        if decision ==1:
            launch_links(results)

        elif decision ==2:

            add_link(result[0][0])
            load_folder(result)

        elif decision == 3:
            main_menu()

def launch_links(links):
    if len(links)==0:
        print("There are currently no links.\n")
        return
    for x in links:
        webbrowser.open(x[1],1)

def add_link(folder_id):
    print("What is the name of the link?")
    link_name = input()
    print("Enter the url: ")
    url = input()
    with connection:
        cursor.execute(ADD_LINK,(link_name,url,folder_id,))


def add_folder():
    folder_name=input("What would you like to name your folder?\n")
    with connection:
        cursor.execute(ADD_FOLDER,(folder_name,))
    print(f"The '{folder_name}' folder has been added to the database.\n")

    main_menu()

def show_folders(results):
    print("Folder ID",end= "       ")
    print("Folder Number")
    print()
    for result in results:
        print(result[0],end= "               ")
        print(result[1])
        print()

def main_menu():
    while True:
        print("Enter 1 to view your folders\nEnter 2 to exit the program\n")
        choice = input()
        try:
            choice = int(choice)
        except:
            print("Invalid input\n")
            continue
        if choice not in {1,2}:
            print("Please enter a valid option.\n")
            continue
        if choice == 1:
            view_folders()
            break
        elif choice == 2:
            print("You will now exit the program. Have a nice day!")
            exit()

main_menu()