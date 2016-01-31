
import threading
import atexit
from application import *
from application.server import *
from application.slave import *
import datetime
import requests
import json
from application.models import *


tries_slave1 = 0
tries_slave2 = 0

tries_master = 0

def thread_function1():
    global test_id
    global completed_boxes
    global progressing_boxes
    global interrupt
    log = get_log()
    print(log)
    print(test_id)
    print('thread_function1')
    print(completed_boxes)
    payload = {}

    payload["datetime"] = str(datetime.datetime.now())
    payload["system_info"] = get_system_info()
    payload["test_id"] = test_id
    payload["call_type"] = 1

    payload['progressing_boxes'] = progressing_boxes
    payload['completed_boxes'] = completed_boxes
    response = requests.post(app.config['MASTER_HOST'] + '/master/slave_update', data=json.dumps(payload))
    response_json = response.json()
    #completed_boxes = {}

    new_test_id = int(response_json['test_id'])
    print(response_json)

    print(interrupt)
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

def thread_function2():
    global test_id
    global completed_boxes
    global progressing_boxes
    global interrupt
    log = get_log()
    print(log)
    print(test_id)
    print('thread_function2')
    print(completed_boxes)
    payload = {}

    payload["datetime"] = str(datetime.datetime.now())
    payload["system_info"] = get_system_info()
    payload["test_id"] = test_id
    payload["call_type"] = 2

    payload['progressing_boxes'] = progressing_boxes
    payload['completed_boxes'] = completed_boxes
    response = requests.post(app.config['MASTER_HOST'] + '/master/slave_update', data=json.dumps(payload))
    response_json = response.json()
    #completed_boxes = {}



def get_latest_commit():

    response = requests.get('https://api.github.com/repos/landregistry-ops/puppet-control')
    response_json = response.json()
    print(response_json)
    if 'pushed_at' in response_json:
        pushed_date = datetime.datetime.strptime(response_json['pushed_at'], "%Y-%m-%dT%H:%M:%SZ")

        test_row = tests.query.filter(tests.test_pushedat == pushed_date).order_by().first()
        if not test_row:
            test_row = tests(pushed_date)
            db.session.add(test_row)
            db.session.commit()
            test_id = test_row.id

            response = requests.get('https://api.github.com/repositories/29131296/contents/hiera/roles')
            response_json2 = response.json()

            num = 50;

            db.session.add(testroles(test_id, 'puppet-master', 1, 1, num))

            for files in response_json2:
                num = num + 1
                db.session.add(testroles(test_id, files['name'].replace('.yaml', ''), 2, 2, num))

            db.session.commit()


            return test_id

        return 0

        print(res)
    else:
        return 0

POOL_TIME_SLAVE1 = 20 #Seconds
POOL_TIME_SLAVE2 = 40 #Seconds
POOL_TIME_MASTER = 120 #Seconds



def interrupt_slave1():
    global yourThread_slave1
    yourThread_slave1.cancel()

def doStuff_slave1():
    global commonDataStruct
    global yourThread_slave1
    global log
    global tries_slave1

    if tries_slave1 == 1:
        # Do your stuff with commonDataStruct Here
        thread_function1()
    else:
        tries_slave1 = 1

    # Set the next thread to happen
    yourThread_slave1 = threading.Timer(POOL_TIME_SLAVE1, doStuff_slave1, ())
    yourThread_slave1.start()

def doStuffStart_slave1():
    # Do initialisation stuff here
    global yourThread_slave1
    # Create your thread
    yourThread_slave1 = threading.Timer(POOL_TIME_SLAVE1, doStuff_slave1, ())
    yourThread_slave1.start()

def interrupt_slave2():
    global yourThread_slave2
    yourThread_slave2.cancel()

def doStuff_slave2():
    global commonDataStruct
    global yourThread_slave2
    global log
    global tries_slave2

    if tries_slave2 == 1:
        # Do your stuff with commonDataStruct Here
        thread_function2()
    else:
        tries_slave2 = 1

    # Set the next thread to happen
    yourThread_slave2 = threading.Timer(POOL_TIME_SLAVE1, doStuff_slave2, ())
    yourThread_slave2.start()

def doStuffStart_slave2():
    # Do initialisation stuff here
    global yourThread_slave2
    # Create your thread
    yourThread_slave2 = threading.Timer(POOL_TIME_SLAVE2, doStuff_slave2, ())
    yourThread_slave2.start()


def interrupt_master():
    global yourThread_master
    yourThread_master.cancel()

def doStuff_master():
    global commonDataStruct
    global yourThread_master
    global log
    global tries_master

    if tries_master == 1:
        # Do your stuff with commonDataStruct Here
        get_latest_commit()
    else:
        tries_master = 1
    # Set the next thread to happen
    yourThread_master = threading.Timer(POOL_TIME_MASTER, doStuff_master, ())
    yourThread_master.start()


if app.config['polling'] == True:
    # Initiate
    doStuffStart_slave1()
    doStuffStart_slave2()

    # When you kill Flask (SIGTERM), clear the trigger for the next thread
    atexit.register(interrupt_slave1)
    atexit.register(interrupt_slave2)

    if app.config['MODE'] == 'master':
        doStuff_master()
