import yaml

class UiMap():
    def __init__(self, path=None):
        self._map = {}
        self.observer = None
        if path: self.load(path)

    def load(self, path):
        with open(path, 'r') as f:
            tree = yaml.load(f)
        for key in tree:
            if key.find('__') != 0:
                self.add_tree(key, tree[key])
        self.driver_name = tree['__driver']
        module_name = 'uimap.drivers.' + self.driver_name
        self.driver = getattr(getattr(__import__(module_name), 'drivers'), self.driver_name).Driver(self)

    def add_tree(self, name, tree, parent=None):
        if type(tree)==dict:
            self.add_control(name, tree['__char'], parent)
            for key in tree:
                if key.find('__') != 0:
                    self.add_tree(key, tree[key], name)
        else:
            self.add_control(name, tree, parent)

    def add_control(self, name, character, parent):
        parent = parent and self._map[parent]
        ctl = Control(self, name, character, parent)
        self._map[name] = ctl
        return ctl

    def all_controls(self):
        return self._map.keys()

    def sendkeys(self, keys):
        return self.driver.sendkeys(None, keys)

    def fire(self, stage, event):
        if self.observer:
            event.stage = stage
            self.observer(event)

    def __getattr__(self, control):
        if control in self._map:
            return self._map[control]
        raise AttributeError(control)

    class Event(object):
        def __init__(self, control, action):
            self.control = control
            self.action  = action
            self.args    = None
            self.stage   = 'find'
            self.ret     = None

class Control():
    def __init__(self, uimap, name, character, parent):
        self.uimap = uimap
        self.parent = parent
        self.name = name
        self.character = character

    def __getattr__(self, action):
        uimap = self.uimap
        driver = uimap.driver
        event = UiMap.Event(self, action)
        if not hasattr(driver, action):
            raise AttributeError()
        uimap.fire('find', event)
        if not driver.wait_exist(self):
            raise Exception(self.name + ' not exist')
        def do_action(*args):
            event.args = args
            uimap.fire('before', event)
            event.ret = getattr(driver, action)(self, *args)
            uimap.fire('done', event)
            return event.ret
        return do_action

    def exist(self):
        return self.uimap.driver.exist(self)

    def wait_exist(self, **kwargs):
        event = UiMap.Event(self, 'wait_exist')
        self.uimap.fire('before', event)
        event.ret = self.uimap.driver.wait_exist(self, **kwargs)
        self.uimap.fire('done', event)
        return event.ret

    def wait_vanish(self, **kwargs):
        event = UiMap.Event(self, 'wait_vanish')
        self.uimap.fire('before', event)
        event.ret = self.uimap.driver.wait_vanish(self, **kwargs)
        self.uimap.fire('done', event)
        return event.ret

    def __str__(self):
        return self.name

    def __repr__(self):
        return '<Control "' + self.name + '">'
