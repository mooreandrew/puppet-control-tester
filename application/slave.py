import multiprocessing
import platform
import socket
import subprocess
import os
from random import randint
from time import sleep
import shlex
from threading import Thread
import yaml

log = 'bb'

test_id = 0

completed_boxes = {}
progressing_boxes = {}

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
    global progressing_boxes
    global completed_boxes
    if server['type'] == 1:
        server_type = '-91.control.net'
    else:
        server_type = '-91.test.net'

    box_name = server['name'] + server_type

    progressing_boxes[server['id']] = server
    progressing_boxes[server['id']]['log'] = ''
    io = subprocess.Popen(shlex.split('vagrant up ' + box_name), cwd='puppet-test-env', stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    for line in io.stdout:
        progressing_boxes[server['id']]['log'] = progressing_boxes[server['id']]['log'] + str(line)
    streamdata = io.communicate()[0]
    exit_code = io.returncode

    if server['type'] == 2:
        os.system("cd puppet-test-env; vagrant destroy " + box_name)

    completed_boxes[server['id']] = server

    completed_boxes[server['id']]['log'] = progressing_boxes[server['id']]['log']
    completed_boxes[server['id']]['exit_code'] = exit_code

    progressing_boxes.pop(server['id'], None)

def remove_completed_servers(servers):
    global completed_boxes
    for key, completed_servers in servers.items():
        print('popping ' + str(key) )
        completed_boxes.pop(int(key), None)

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

    return {'system': platform.system(), 'distribution': linux_distribution()[0], 'version': linux_distribution()[1], 'cores': multiprocessing.cpu_count(), 'hostname': socket.gethostname(), 'ip': socket.gethostbyname(socket.gethostname())}


def destroy_all_vms():

    os.system("cd puppet-test-env; vagrant destroy  --force puppet-master-91.control.net")

    if os.path.isfile("puppet-test-env/servers.yaml"):
        with open("puppet-test-env/servers.yaml", 'r') as stream:
            steam_yaml = yaml.load(stream)
            print(steam_yaml)
            if len(steam_yaml['servers']) > 0:
                for server in steam_yaml['servers']:
                    os.system("cd puppet-test-env; vagrant destroy --force " + list(server.keys())[0])

def reset_serversyaml():
    f = open("puppet-test-env/servers.yaml",'w')
    f.write('servers:\n')
    f.close()

def write_serversyaml(servers):
    for server in servers:
        if server['type'] == 2:
            f = open("puppet-test-env/servers.yaml",'a')
            f.write('  - ' + server['name'] + '-91.test.net:\n')
            f.write('      ip: 192.16.42.' + str(server['ip']) + '\n')
            f.write('      clone: false\n')
            f.write('      test: true\n')
            f.write('      machine_location: zone1\n')
            f.write('      machine_role: ' + server['name'] + '\n')
            f.write('      puppet_environment: development\n')
            f.close()

    #
# servers:
#   - gitlab-app-91.test.net:
#       ip: 192.16.42.51
#       clone: false
#       test: true
#       machine_location: zone1
#       machine_role: gitlab-app
#       puppet_environment: development
#
