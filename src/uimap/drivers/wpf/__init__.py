import time
import os
from os import path
import subprocess
import xmlrpclib
import socket

import uimap.wait as wait

SERVICE_PY = path.join(path.dirname(path.realpath(__file__)), "service.py")
ACTION_SET = set(['click', 'set_value', 'exist', 'sendkeys', 'activate', 'get_property', 'maximize', 'value', 'close'])
class Driver():
    def __init__(self, uimap):
        self._uimap = uimap
        self._start_service()

    def _start_service(self, restart=False):
        if restart: subprocess.call(['taskkill', '/im', 'ipy.exe'])
        subprocess.Popen("ipy " + SERVICE_PY)
        self._server = xmlrpclib.ServerProxy("http://127.0.0.1:1337", allow_none=True)
        alive = False
        while not alive:
            try:
                time.sleep(1)
                alive = self._server.alive()
            except:
                pass

        self._ready_controls = set()
        for k in self._uimap._map:
            self._wpf_set_info(self._uimap._map[k])

    def _stop_service(self):
        os.system("taskkill /im ipy.exe /f")

    def __getattr__(self, action):
        if not action in ACTION_SET:
            raise AttributeError(action)
        def do_action(control, *args):
            name = control and control.name
            retries = 3
            while retries > 0:
                try:
                    retries -= 1
                    succ, data = self._server.action(action, name, *args)
                    if not succ and data == 'no_info':
                        self._start_service()
                    else:
                        break
                except socket.error:
                    self._start_service(True)
            if succ:
                time.sleep(0.2)
                return data
            else:
                raise Exception(data)
        return do_action

    def _wpf_set_info(self, control):
        if control.name in self._ready_controls:
            return
        if control.parent:
            self._wpf_set_info(control.parent)
            parent = control.parent.name
        else:
            parent = None
        self._server.set_info(control.name, control.character, parent)

    def wait_exist(self, control, **kwargs):
        return wait.wait_exist(control, **kwargs)

    def wait_vanish(self, control, **kwargs):
        return wait.wait_vanish(control, **kwargs)

    def select_item(self, control, index):
        self.sendkeys(control, '<home>' + '<down>' * index + '<enter>')
