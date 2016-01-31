
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
    global test_id


    global completed_boxes
    global progressing_boxes

    log = get_log()
    print(log)
    print(test_id)
    print('thread_function')
    print(completed_boxes)
    payload = {}

    payload["datetime"] = str(datetime.datetime.now())
    payload["system_info"] = get_system_info()
    payload["test_id"] = test_id
    payload['progressing_boxes'] = progressing_boxes
    payload['completed_boxes'] = completed_boxes
    response = requests.post(app.config['MASTER_HOST'] + '/master/slave_update', data=json.dumps(payload))
    response_json = response.json()
    #completed_boxes = {}

    new_test_id = int(response_json['test_id'])

    if (new_test_id != test_id):
        clone_repo()
        destroy_all_vms()
        reset_serversyaml()
        # start
        test_id = new_test_id

    remove_completed_servers(response_json['completed_boxes'])

    write_serversyaml(response_json['test_roles'])
    start_vms(response_json['test_roles'])


    print(response_json)

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
