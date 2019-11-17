import pysftp
import datetime
import json
import os


def checkInt(i):
    r = True
    try:
        int(i)
        r = True
    except ValueError:
        return False
    r = int(i) < 0 or int(i) > 5
    return r


def getFiles():
    os.rename("cache-dir-prev", "cache-dir_" + ts)
    os.rename("cache-dir", "cache-dir-prev")
    os.mkdir("cache-dir")
    with pysftp.Connection(config["environments"]["frontend"]["ip"], username="kevin", password="kevin") as c1:
        for i in config["environments"]["frontend"]["subdirs"]:
            c1.get_r(i, "cache-dir/" + i)

    with pysftp.Connection(config["environments"]["database"]["ip"], username="it490user", password="prodinfo") as c2:
        for i in config["environments"]["frontend"]["subdirs"]:
            c2.get_r(i, "cache-dir/" + i)

    with pysftp.Connection(config["environments"]["rabbitmq"]["ip"], username="faddy", password="faddy") as c3:
        for i in config["environments"]["frontend"]["subdirs"]:
            c3.get_r(i, "cache-dir/" + i)

    with pysftp.Connection(config["environments"]["dmz"]["ip"], username="anthony", password="anthony") as c4:
        for i in config["environments"]["frontend"]["subdirs"]:
            c4.get_r(i, "cache-dir/" + i)
    print("Cache Directory updated")


def pushFiles(flag):
    if flag == "P":  # Promotion
        sourcedir = "cache-dir"
    if flag == "R":  # Revert to Last
        sourcedir = "cache-dir-prev"
    with pysftp.Connection(config["environments"]["frontend"]["ip"], username="kevin", password="kevin") as c1:
        for i in config["environments"]["frontend"]["subdirs"]:
            c1.remove(sourcedir + "/" + i)
            c1.put_r(sourcedir + "/" + i, i)

    with pysftp.Connection(config["environments"]["database"]["ip"], username="it490user", password="prodinfo") as c2:
        for i in config["environments"]["frontend"]["subdirs"]:
            c2.remove(sourcedir + "/" + i)
            c2.put_r(sourcedir + "/" + i, i)

    with pysftp.Connection(config["environments"]["rabbitmq"]["ip"], username="faddy", password="faddy") as c3:
        for i in config["environments"]["frontend"]["subdirs"]:
            c3.remove(sourcedir + "/" + i)
            c3.put_r(sourcedir + "/" + i, i)

    with pysftp.Connection(config["environments"]["dmz"]["ip"], username="anthony", password="anthony") as c4:
        for i in config["environments"]["frontend"]["subdirs"]:
            c4.remove(sourcedir + "/" + i)
            c4.put_r(sourcedir + "/" + i, i)


# Get my globals in order
config_tmp = open("config/environments.json", "r")
config = json.loads(config_tmp)
config_tmp.close()
ts_tmp = datetime.now()
ts = ts_tmp.strftime("%Y%m%d_%H%M%S")

# menu: select push, pull, revert, view versions
print("Welcome to the IT490 Code Promotion System. I couldn't find anything that did the thing I needed out of the box")
print("  so I wrote my own! ")
print(" ")
keepgoing = True
while keepgoing:
    print("--------------------------------------------------------------")
    print("--Please listen carefully, as our menu options have changed---")
    print("--------------------------------------------------------------")
    print(" 0. Exit")
    print(" 1. View Versions List")
    print(" 2. Pull Code from Environment")
    print(" 3. Push Code To Environment")
    print(" 4. Revert Code in Environment to previous build")
    print("-------------------------------------------------------------")
    txt = input("Your Choice: ")
    user_input_test = checkInt(txt)
    if not user_input_test:
        print("You fool. You absolute moron. What's wrong with you. That is not a valid selection.")
    else:
        u = int(txt)
        if u == 0:
            print("OK bye....")
            keepgoing = False
        elif u == 1:
            # print list of all the directories
            False
        elif u == 2:
            print("Attempting to pull the code in from the various VM's.")
            getFiles()
        elif u == 3:
            print("Hey - make sure you pulled before you push! Type STOP to go do that now, any other text entry will "
                  "continue this process")
            txt2 = input("Speak now or forever hold your peace: ")
            if txt2.upper() == "STOP":
                print("Aren't you glad I stopped you?")
            else:
                print("THE CONTRACT IS SEALED")
                pushFiles("P")
        elif u == 4:
            print("Hey - you're about to roll back the code in the current environment to whatever the last version "
                  "was. Type STOP cancel, any other text entry will continue this process")
            txt2 = input("Speak now or forever hold your peace: ")
            if txt2.upper() == "STOP":
                print("Aren't you glad I stopped you?")
            else:
                print("THE CONTRACT IS SEALED")
                pushFiles("R")
