import multiprocessing
import platform
import socket
import subprocess
import os
from random import randint
from time import sleep
import shlex
from threading import Thread

log = 'bb'

test_id = 0

progressing_boxes = {}

completed_boxes = {}

def get_log():
    return log

def set_log(logt):
    global log
    log = log + logt

def clone_repo():
    #subprocess.call(["git", "clone", "https://github.com/LandRegistry-Ops/puppet-test-env", clone_dir + "puppet-control"])
    #sleep(randint(1,5))
    #os.system("rm -rf puppet-test-env")

    if os.path.isdir("puppet-test-env"):
        os.system("cd puppet-test-env; git pull")
    else :
        os.system("git clone https://github.com/LandRegistry-Ops/puppet-test-env")



def vagrant_command(server):

    if server['type'] == 1:
        server_type = '-91.control.net'
    else:
        server_type = '-91.test.net'

    box_name = server['name'] + server_type

    progressing_boxes[server['id']] = server
    progressing_boxes[server['id']]['log'] = ''
    io = subprocess.Popen(shlex.split('vagrant up ' + box_name), cwd='puppet-test-env', stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    for line in io.stdout:
        print(str(line.strip()))
        progressing_boxes[server['id']]['log'] = progressing_boxes[server['id']]['log'] + str(line)
    streamdata = io.communicate()[0]
    exit_code = io.returncode

    if server['type'] == 2:
        os.system("cd puppet-test-env; vagrant destroy " + box_name)

    progressing_boxes.pop(server['id'], None)

    completed_boxes[server['id']]['log'] = str(line)
    completed_boxes[server['id']]['exit_code'] = exit_code

    print(exit_code)


def start_vms(servers):

    for server in servers:
        # TODO: Append on to puppet-test-env/servers.yaml the new server to start (if not a control server)

        thread = Thread(target = vagrant_command, args = ([server]))
        thread.start()
        #thread.join()
        #vagrant_command('vagrant up puppet-master-91.control.net')


def linux_distribution():
  try:
    return platform.linux_distribution()
  except:
    return [platform.system(), platform.release()]

def get_system_info():

    # Update slave, set details
    #


    return {'system': platform.system(), 'distribution': linux_distribution()[0], 'version': linux_distribution()[1], 'cores': multiprocessing.cpu_count(), 'hostname': socket.gethostname(), 'ip': socket.gethostbyname(socket.gethostname())}
