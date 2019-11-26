import pysftp
import datetime
import json
import os


def checkInt(i, lo, hi):
    r1 = True
    try:
        int(i)
        r1 = (hi >= int(i) >= lo)
    except ValueError:
        return False
    return r1


def getFiles():
    if os.path.exists("cache-dir"):
        os.rmdir("cache-dir")

    os.mkdir("cache-dir")
    c1 = pysftp.Connection(config["environments"]["frontend"]["ip"],
                           username=config["environments"]["frontend"]["sftp_user"],
                           password=config["environments"]["frontend"]["sftp_pw"], cnopts=cnopts)
    for i in config["environments"]["frontend"]["subdirs"]:
        d = config["environments"]["frontend"]["codepath"]
        # print(d)
        os.mkdir("cache-dir/" + i)
        # print("cache-dir/"+i)
        c1.chdir(d)
        c1.get_r(i, "cache-dir")
        # print("done with "+i)

    c2 = pysftp.Connection(config["environments"]["database"]["ip"],
                           username=config["environments"]["database"]["sftp_user"],
                           password=config["environments"]["database"]["sftp_pw"], cnopts=cnopts)
    for i in config["environments"]["database"]["subdirs"]:
        d = config["environments"]["database"]["codepath"]
        # print(d)
        os.mkdir("cache-dir/" + i)
        # print("cache-dir/" + i)
        c2.chdir(d)
        c2.get_r(i, "cache-dir")
        # print("done with " + i)

    c3 = pysftp.Connection(config["environments"]["rabbitmq"]["ip"],
                           username=config["environments"]["rabbitmq"]["sftp_user"],
                           password=config["environments"]["rabbitmq"]["sftp_pw"], cnopts=cnopts)
    for i in config["environments"]["rabbitmq"]["subdirs"]:
        d = config["environments"]["rabbitmq"]["codepath"]
        # print(d)
        os.mkdir("cache-dir/" + i)
        # print("cache-dir/" + i)
        c3.chdir(d)
        c3.get_r(i, "cache-dir")
        # print("done with " + i)

    c4 = pysftp.Connection(config["environments"]["dmz"]["ip"],
                           username=config["environments"]["dmz"]["sftp_user"],
                           password=config["environments"]["dmz"]["sftp_pw"], cnopts=cnopts)
    for i in config["environments"]["dmz"]["subdirs"]:
        d = config["environments"]["dmz"]["codepath"]
        os.mkdir("cache-dir/" + i)
        c4.chdir(d)
        c4.get_r(d, "cache-dir")
    print("Cache Directory updated")
    c1.close()
    c2.close()
    c3.close()
    c4.close()
    version_id = "ver__" + ts
    os.rename("cache-dir", version_id)
    print("new version stored: " + version_id)
    fi = open("last_pull.txt", "wt")
    fi.write(version_id)
    fi.close()


def pushFiles(flag):
    ver = []
    i = 0
    for dirs in os.listdir():
        if "ver__" in dirs and os.listdir(dirs):
            # If the directory is empty or not named ver__* (we dont want to push config lol) then dont
            # display it
            # print(str(i) + "-  /" + dirs)
            ver.append(dirs)
            i += 1
    print(" ")
    if i == 0:
        print("There's no code pulled into the repository, try doing that first")
        return 0
    if flag == "P":  # Promotion
        fi = open("config/last_pull.txt", "rt")
        sourcedir = fi.readline()
        fi.close()
    elif flag == "R":  # Revert to Last
        fi = open("config/revert_push.txt", "rt")
        sourcedir = fi.readline()
        fi.close()
    else:
        sourcedir = flag

    # still need to test this
    c1 = pysftp.Connection(config["environments"]["frontend"]["ip"],
                           username=config["environments"]["frontend"]["sftp_user"],
                           password=config["environments"]["frontend"]["sftp_pw"], cnopts=cnopts)
    for i in config["environments"]["frontend"]["subdirs"]:
        d = config["environments"]["frontend"]["codepath"]
        c1.chdir(d)
        c1.remove(i)
        c1.mkdir(i)
        c1.put_r(i, i)

    c2 = pysftp.Connection(config["environments"]["database"]["ip"],
                           username=config["environments"]["database"]["sftp_user"],
                           password=config["environments"]["database"]["sftp_pw"], cnopts=cnopts)
    for i in config["environments"]["frontend"]["subdirs"]:
        d = config["environments"]["database"]["codepath"]
        c2.chdir(d)
        c2.remove(i)
        c2.mkdir(i)
        c2.put_r(i, i)

    c3 = pysftp.Connection(config["environments"]["rabbitmq"]["ip"],
                           username=config["environments"]["rabbitmq"]["sftp_user"],
                           password=config["environments"]["rabbitmq"]["sftp_pw"], cnopts=cnopts)
    for i in config["environments"]["frontend"]["subdirs"]:
        d = config["environments"]["rabbitmq"]["codepath"]
        c3.chdir(d)
        c3.remove(i)
        c3.mkdir(i)
        c3.put_r(i, i)

    c4 = pysftp.Connection(config["environments"]["dmz"]["ip"],
                           username=config["environments"]["dmz"]["sftp_user"],
                           password=config["environments"]["dmz"]["sftp_pw"], cnopts=cnopts)
    for i in config["environments"]["frontend"]["subdirs"]:
        d = config["environments"]["dmz"]["codepath"]
        c4.chdir(d)
        c4.remove(i)
        c4.mkdir(i)
        c4.put_r(i, i)

    fi_revert = open("config/revert_push.txt", "wt")
    fi_push = open("config/last_push.txt", "wt")
    revert_ver = fi_push.readline()
    fi_revert.write(revert_ver)
    fi_push.write(sourcedir)
    fi_push.close()
    fi_revert.close()


# Get my globals in order
cwd = os.getcwd()
with open(cwd + '/config/environments.json') as config_tmp:
    # config_tmp = open("config/environments.json", "r")
    config = json.load(config_tmp)

cnopts = pysftp.CnOpts()
cnopts.hostkeys = None

# menu: select push, pull, revert, view versions
print("Welcome to the IT490 Code Promotion System. I couldn't find anything that did the thing I needed out of the box")
print("  so I wrote my own! ")
print(" ")
keepgoing = True
while keepgoing:
    ts_tmp = datetime.datetime.now()
    ts = ts_tmp.strftime("%Y%m%d_%H%M%S")
    print("--------------------------------------------------------------")
    print("--Please listen carefully, as our menu options have changed---")
    print("--------------------------------------------------------------")
    print(" 0. Exit")
    print(" 1. View Versions List")
    print(" 2. Pull Code From Environment to VC")
    print(" 3. Push Code To Environment to VC (most recent)")
    print(" 4. Revert Code in Environment to the previous build")
    print(" 5. Revert Code in Environment to a specific build")
    print("-------------------------------------------------------------")
    txt = input("Your Choice: ")
    user_input_test = checkInt(txt, 0, 5)
    if not user_input_test:
        print("You fool. You absolute moron. What's wrong with you. That is not a valid selection.")
    else:
        u = int(txt)
        if u == 0:
            print("OK bye....")
            keepgoing = False
        elif u == 1:
            for dirs in os.listdir():
                if "ver__" in dirs and os.listdir(dirs):
                    print(dirs)
            print(" ")
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
        elif u == 5:
            ver = []
            i = 0
            for dirs in os.listdir():
                if "ver__" in dirs and os.listdir(dirs):
                    # If the directory is empty or not named ver__* (we dont want to push config lol) then dont
                    # display it
                    print(str(i) + "-  /" + dirs)
                    ver.append(dirs)
                    i += 1
            print(" ")
            if i == 0:
                print("I do not have any saved code to show you. Try pulling first.")
                continue
            print(" So which one do you want to deploy?")
            txt3 = input("Select an index number")
            r = checkInt(txt3, 0, (i - 1))
            if not r:
                print("You fucking moron. You absolute trashheap. You FOOL. You come into MY HOUSE? You don't deserve "
                      "to deploy code.")
                continue
            else:
                print(
                    "Hey - you're about to roll back the code in the current environment to whatever the version "
                    "you chose was. Type STOP cancel, any other text entry will continue this process")
                txt4 = input("Speak now or forever hold your peace: ")
                if txt4.upper() == "STOP":
                    print("Aren't you glad I stopped you?")
                else:
                    print("THE CONTRACT IS SEALED")
                    pushFiles(ver[txt3])
