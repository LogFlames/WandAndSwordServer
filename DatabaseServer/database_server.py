import time
import socket
import struct
import hashlib
import os
import configparser

USER_FOLDER = "USERS"

path_to_users = os.path.join(os.path.dirname(__file__), USER_FOLDER)

def addUser(name, password):
    foundFile = False
    try:
        with open(os.path.join(path_to_users, name + ".ini"), "r"):
            foundFile = True
    except:
        foundFile = False
    
    if foundFile:
        return False

    with open(os.path.join(path_to_users, name + ".ini"), "w+"):
        pass
    
    config = configparser.ConfigParser()
    config.read(USER_FOLDER + name + ".ini")
    config['Credentials']['password'] = password

    with open(os.path.join(path_to_users, name + ".ini", 'w') as configfile:
        config.write(configfile)
    
    return True

def checkLogin():
    pass

print(addUser("Pelle", "abc123"))