import psycopg2 as pg2
import os
import webbrowser
import time


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
        print("\nThere are currently no folders.\n")
    else:
        show_folders(results)

    while True:
        print("Enter 1 to select a folder\nEnter 2 to add a folder\nEnter 3 to go to the Main Menu")
        decision = input()
        try:
            decision = int(decision)
        except:
            print("\nInvalid input.\n")
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


        folder_choice = input("\nEnter the Folder ID of the folder you would like to select:\n")

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
            load_folder(result[0][0])
            break

def load_folder(result):
    with connection:
        cursor.execute("SELECT * from folder WHERE folder_id = %s;",(result,))
        folder_name = cursor.fetchall()

    print(f"\nFolder ID: {result}",end="          ")
    print(f"Folder Name: {folder_name[0][1]}")
    print("\n")
    with connection:
        cursor.execute("""SELECT link_name,url FROM link JOIN folder on link.folder_id = folder.folder_id WHERE folder.folder_id = %s;""",(result,))
        results = cursor.fetchall()

    if len(results) == 0:
        print("There are currently no links in the Group.\n")
    else:

        print("Link Name:",end="         ")
        print("Link URL:")
        print()

        for x in results:
            print(x[0],end="               ")
            print(x[1])
            print()

    while True:
        decision = input("Enter 1 to launch the links\nEnter 2 to add a link the the Group\nEnter 3 to delete a link from the Bookmark Group\nEnter 4 to go to the Main Menu\nEnter 5 to delete the Bookmark Group\n")

        try:
            decision = int(decision)
        except:
            print("Invalid input.\n")
        if decision not in {1,2,3,4,5}:
            print("\nPlease select a valid option.\n")
            continue

        if decision ==1:
            launch_links(results)

        elif decision ==2:

            add_link(result)
            load_folder(result)

        elif decision == 3:
            
            delete_link(result)

        elif decision ==4:
            main_menu()

        elif decision ==5:
            delete_folder(result)

def delete_folder(result):

    while True:

        print("A\nre you sure you want to delete the folder? Your folder and links will be permantly removed.\n\nIf you would like to proceed with deletion, enter 'delete'. Enter either 'cancel' or 'go back' to return to the previous menu.\n\n")

        deletion_decision = input()

        go_back_choices ={'cancel','go back'}
        
        if deletion_decision in go_back_choices:
            load_folder(result)
            break

        if deletion_decision == 'delete':
            with connection:
                cursor.execute("DELETE FROM link cascade WHERE folder_id = %s;",(result,))
                cursor.execute("DELETE FROM folder cascade WHERE folder_id = %s;",(result,))
            print("Your folder has been deleted, and you will now be returned to the main menu.\n\n")
            time.sleep(2)
            break
    main_menu()


def delete_link(folder_number):

    while True:
    
        print("\nEnter the name of the link you would like to delete, or enter 'go back' to cancel your deletion and be returned to the previous page:\n")

        delete_choice = input()

        if delete_choice == 'go back':
            print("Your deletion will be cancelled, and you will return to the previous page.\n\n")
            time.sleep(2.2)
            load_folder(folder_number)
            break

        with connection:
            cursor.execute("SELECT * FROM link where link_name = %s;",(delete_choice,))
            results = cursor.fetchall()

        if len(results) == 0:
            print("\nThere is no link with that foler name.\n\n")
            continue

        else:

            print("\nAre you sure you would like to delete the link from this Bookmark Group?\n\nType 'delete' to confirm this removal.\nType 'cancel' to keep the link and return to the previous screen.\n")

            confirm_or_go_back = input().lower()

            if confirm_or_go_back == 'delete':
                print("Your link will now be removed from the Bookmark Group.\n\n")
                time.sleep(2)
                with connection:
                    cursor.execute("DELETE FROM link where link_name = %s;",(delete_choice,))

                print("The link has been removed.")
                time.sleep(1.3)

                load_folder(folder_number)


            else:
                print("Okay, this deletion will be cancelled and you will be returned to the previous menu.\n")
                time.sleep(2.5)
                load_folder(folder_number)

        
def launch_links(links):
    if len(links)==0:
        print("\nThere are currently no links.\n")
        return
    else:
        for x in links:
            webbrowser.open(x[1],1)

        print("Your links have been launched in your default web browser.You will be returned to the Main Menu.\n")
        time.sleep(2)
        main_menu()
def add_link(folder_id):
    while True:
        print("\nWhat is the name of the link?")
        link_name = input().strip()

        with connection:
            cursor.execute("SELECT * FROM link;")
            results = cursor.fetchall()
            
        names =[result[1] for result in results]
        
        if link_name in names:
            print("You already have a link with that name. Please use a different name.")
            continue

        else:
            break

    print("\nEnter the url: ")
    url = input()
    with connection:
        cursor.execute(ADD_LINK,(link_name,url,folder_id,))


def add_folder():
    folder_name=input("\nWhat would you like to name your folder?\n")
    with connection:
        cursor.execute(ADD_FOLDER,(folder_name,))
    print(f"\nThe '{folder_name}' folder has been added to the database.\n")
    time.sleep(.5)

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

        print("\nEnter 1 to view your folders\nEnter 2 to exit the program\n")
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