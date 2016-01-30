import multiprocessing
import platform
import socket

log = 'bb'

def get_log():
    return log

def set_log(logt):
    global log
    log = log + logt


def linux_distribution():
  try:
    return platform.linux_distribution()
  except:
    return [platform.system(), platform.release()]

def get_system_info():

    # Update slave, set details
    #


    return {'system': platform.system(), 'distribution': linux_distribution()[0], 'version': linux_distribution()[1], 'cores': multiprocessing.cpu_count(), 'hostname': socket.gethostname(), 'ip': socket.gethostbyname(socket.gethostname())}
