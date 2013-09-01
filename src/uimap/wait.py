import time

default_timeout = 30
default_interval = 1
listeners = set()

class Wait():
    def __init__(self, timeout=default_timeout, interval=default_interval, listeners=[]):
        self.started_at = 0
        self.timeout    = timeout
        self.interval   = interval
        self.finished     = False
        self.result     = None
        self.listeners  = listeners
        self._data      = None

    def rec_start(self):
        self.started_at = time.time()
        self.expires_at = self.started_at + self.timeout

    def rec_stop(self):
        self.stopped_at = time.time()

    @property
    def duration(self):
        return self.stopped_at - self.started_at

    @property
    def elapsed(self):
        return time.time() - self.started_at

    @property
    def expired(self):
        return time.time() > self.expires_at

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, value):
        self._data = value

    def defer(self, value):
        self.expires_at += value

    def finish(self, result=None):
        self.finished = True
        self.result  = result

    def till(self, proc, *args):
        self.rec_start()
        while not self.expired:
            time.sleep(self.interval)
            proc(self, *args)
            if self.finished: break
            self.check_listeners()
        self.rec_stop()
        return self

    def check_listeners(self):
        listener_set = set()
        listener_set.update(listeners)
        listener_set.update(self.listeners)
        for proc in listener_set:
            if proc: proc(self)

def wait_till(proc, *args, **kwargs):
    return Wait(**kwargs).till(proc, *args)

def wait_one_of(*controls, **kwargs):
    return wait_till(_find_one_of, *controls, **kwargs).result

def wait_exist(control, **kwargs):
    return bool(wait_one_of(control, **kwargs))

def wait_vanish(control, gap_allowance=2, **kwargs):
    def proc(wait, control, gap_allowance):
        if control.exist():
            wait.data = None
        elif wait.data:
            if time.time() - wait.data > gap_allowance:
                wait.finish()
        else:
            wait.data = time.time()
    return wait_till(proc, control, gap_allowance, **kwargs).finished

def _find_one_of(wait, *controls):
    ctl = find_one_of(*controls)
    if ctl:
        wait.finish(ctl)

def find_one_of(*controls):
    for control in controls:
        if control.exist():
            return control

def add_listener(proc):
    listeners.update([proc])

def del_listener(proc):
    try:
        listeners.remove(proc)
    except KeyError:
        pass
