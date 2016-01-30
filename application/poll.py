
import threading
import atexit
from application import *
from application.server import *
import multiprocessing

log = 'bb'


def get_log():
    return log

def set_log(logt):
    global log
    log = log + logt

def get_cores():
    cores = multiprocessing.cpu_count()
    return cores



def thread_function():
    log = get_log()

    # Send message to the master.
    # - I'm alive
    # - Current test id (if this doesn't match server, then to stop all tests)
    # - How many cores
    # - The completed tests (and their status)
    # - The active tests
    # - Any logs

    print(log)


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

    # Do your stuff with commonDataStruct Here
    thread_function()

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
