import os
import glob

def deleteLogs():
    folder = 'logs/'
    excluded_file = '.gitkeep'
    for file in glob.glob(folder + '*'):
        if os.path.basename(file) != excluded_file:
            os.remove(file)
    print("Logs deletion complete.")

def deleteDB():
    os.remove('database.db')
    print("Database deletion complete.")

def clearTerminal():
    try:
        os.system('cls')
    except:
        pass
    try:
        os.system('clear')
    except:
        pass

while True:
    print("To delete the DB enter   : 2")
    print("To delete the logs enter : 1")
    print("To exit enter            : 0")
    ask = input("What would you like to do? " )
    if ask == "0":
        clearTerminal()
        exit()
    elif ask == "1":
        deleteLogs()
    elif ask == "2":
        deleteDB()
    clearTerminal()