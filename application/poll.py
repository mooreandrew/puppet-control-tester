
import threading
import atexit
from application import *
from application.server import *
from application.slave import *
import datetime
import requests
import json


tries = 0


def thread_function():
    log = get_log()
    print(log)

    payload = {"status":1,"datetime": str(datetime.datetime.now()), "system_info": get_system_info()}

    response = requests.post(app.config['MASTER_HOST'] + '/master/slave_update', data=json.dumps(payload))
    response_json = response.json()

    print(response_json)
    # Send message to the master.
    # - I'm alive
    # - Current test id (if this doesn't match server, then to stop all tests)
    # - How many cores
    # - The completed tests (and their status)
    # - The active tests
    # - Any logs



POOL_TIME = 5 #Seconds


# variables that are accessible from anywhere
commonDataStruct = {}
# lock to control access to variable
dataLock = threading.Lock()
# thread handler

def interrupt():
    global yourThread
    yourThread.cancel()

def doStuff():
    global commonDataStruct
    global yourThread
    global log
    global tries

    if tries == 1:
        # Do your stuff with commonDataStruct Here
        thread_function()
    else:
        tries = 1
    # Set the next thread to happen
    yourThread = threading.Timer(POOL_TIME, doStuff, ())
    yourThread.start()

def doStuffStart():
    # Do initialisation stuff here
    global yourThread
    # Create your thread
    yourThread = threading.Timer(POOL_TIME, doStuff, ())
    yourThread.start()



if app.config['polling'] == True:
    # Initiate
    doStuffStart()
    # When you kill Flask (SIGTERM), clear the trigger for the next thread
    atexit.register(interrupt)
