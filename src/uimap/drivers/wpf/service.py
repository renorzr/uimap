import subprocess
import traceback
import sys
import os
from SimpleXMLRPCServer import SimpleXMLRPCServer as Server

PID_FILE = 'c:\wpf_service.pid'
try:
    with file(PID_FILE, 'r') as f:
        pid = f.read()
        proc = subprocess.Popen(['tasklist', '/fi', 'imagename eq ipy.exe', '/fi', 'pid eq ' + str(pid)], stdout=subprocess.PIPE)
        while True:
            line = proc.stdout.readline()
            if not line:
                break
            if line.find('ipy.exe') != -1:
                print 'server is already running'
                exit(1)
except IOError:
    pass

print 'pid:', str(os.getpid())
with file(PID_FILE, 'w') as f:
    f.write(str(os.getpid()))

import actions

def action(action_name, name, *args):
    if actions.set_info.no_info:
        return False, 'no_info'
    try:
        print(action_name, name, args)
        if (action_name == 'exist'):
            return True, actions.exist(name)
        proc = getattr(actions, action_name)
        return True, actions.action(proc, name, args)
    except:
        print str(sys.exc_info()[1])
        return False, str(sys.exc_info()[1])

def alive():
    return True

server = Server(('127.0.0.1',1337))
server.register_function(action)
server.register_function(actions.set_info)
server.register_function(alive)
server.serve_forever()
