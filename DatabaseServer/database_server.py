import time
import socket
import struct
import hashlib
import os
import configparser

USER_FOLDER = "USERS"

path_to_script = os.path.dirname(__file__)
path_to_users = os.path.join(path_to_scipt, USER_FOLDER)

def addUser(name, password):
    foundFile = False
    try:
        with open(os.path.join(path_to_users, name + ".ini"), "r"):
            foundFile = True
    except:
        foundFile = False
    
    if foundFile:
        return False

    with open(os.path.join(path_to_users, name + ".ini"), "w+") as f:
        with open(os.path.join(path_to_script, "default.ini"), "r") as default_ini_file:
            for line in default_ini_file:
                f.write(line)
    
    config = configparser.ConfigParser()
    config.read(USER_FOLDER + name + ".ini")
    config['Credentials']['password'] = password

    with open(os.path.join(path_to_users, name + ".ini", 'w') as configfile:
        config.write(configfile)
    
    return True

def checkLogin():
    pass

print(addUser("Pelle05", "abc123"))