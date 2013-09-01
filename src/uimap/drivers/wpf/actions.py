import re
import sys
import traceback
import clr
import ctypes
import time

sys.path.append(r"C:\Program Files\IronPython 2.7\Lib")
sys.path.append(r"C:\Program Files\Reference Assemblies\Microsoft\Framework\.NETFramework\v4.0\Profile\Client")
clr.AddReferenceToFile("UIAutomationClient.dll")
clr.AddReferenceToFile("UIAutomationTypes.dll")
clr.AddReferenceToFile("System.windows.Forms.dll")
clr.AddReferenceToFile("mscorlib.dll")
from System.Windows.Automation import *
from System.Windows.Forms import *
from System import *
MOUSEEVENT_LEFTDOWN = 0x02
MOUSEEVENT_LEFTUP   = 0x04
MOUSEEVENT_MOVE     = 0x8001

def _create_prop(prop):
    return getattr(AutomationElement, prop + 'Property')

def _prop_cond(prop, val):
    if prop == 'ControlType':
        val = getattr(ControlType, val)
    prop = _create_prop(prop)
    if isinstance(val, str):
        val = val.replace(r'\n', u'\n')
    return PropertyCondition(prop, val)

ELEMENT_EXPIRATION = 5 # secs
PROP_ID = _create_prop('AutomationId')
SCP_DESCE = TreeScope.Descendants
SCP_CHILD = TreeScope.Children
DEF_SCOPE = SCP_DESCE
SCOPES = {
    'child': SCP_CHILD,
    'desce': SCP_DESCE,
    'children': SCP_CHILD,
    'descendants': SCP_DESCE,
        }

controls = {}

class Control():
    def __init__(self, name, character, parent):
        self.name = name
        self.character = character
        self.parent = parent and controls[parent]
        self.element = None
        window = self.parent
        while window and window.parent:
            window = window.parent
        self.window = window
        self.make_condition()
        self.expire_at = 0

    def find(self, force_expire=False):
        if self.available(force_expire): return self.element
        print 'find', self.name, force_expire
        if self.parent:
            root = self.parent.find()
        else:
            root = AutomationElement.RootElement
        if not root: return None
        if isinstance(self.condition, LdtpCondition):
            self.element = self.condition.find()
        else:
            self.element = root.FindFirst(self.scope, self.condition)
        self.expire_at = time.time() + ELEMENT_EXPIRATION
        return self.element

    def available(self, force_expire=False):
        if not self.element: return False
        return not force_expire and time.time() < self.expire_at

    def make_condition(self):
        self.condition = LdtpCondition.create(self)
        if self.condition: return

        conditions = []
        for prop_name in self.character:
            if prop_name.find('__') != 0:
                value = self.character[prop_name]
                condition = _prop_cond(prop_name, value)
                conditions.append(condition)
        if len(conditions) > 1:
            self.condition = AndCondition(*conditions)
        else:
            self.condition = conditions[0]
        self.scope = SCOPES[self.character.get('__scope', 'desce')]

    def get_pattern(self, pattern):
        ele = self.find()
        if not ele:
            raise ElementNotAvailableException
        return ele.GetCurrentPattern(pattern.Pattern)

    def get_property(self, prop_name):
        prop = _create_prop(prop_name)
        return self.find().GetCurrentPropertyValue(prop)

    def value(self):
        typ = None
        if isinstance(self.condition, LdtpCondition):
            typ = self.condition.typ
        if typ == 'txt':
            return self.get_pattern(ValuePattern).Current.Value
        return self.get_property('Name')

class LdtpCondition():
    TYPES = {
            'txt': _prop_cond('ControlType', 'Edit'),
            'lbl': _prop_cond('ControlType', 'Text'),
            'btn': _prop_cond('ControlType', 'Button'),
            'chk': _prop_cond('ControlType', 'CheckBox'),
            'mnu': _prop_cond('ControlType', 'Menu'),
            'mni': _prop_cond('ControlType', 'MenuItem'),
            'cbo': _prop_cond('ControlType', 'ComboBox'),
            '???': Condition.TrueCondition,
            }

    def __init__(self, window, typ, desc, index):
        self.window = window
        self.typ    = typ
        self.desc   = desc
        self.index  = index
        self.condition = self.__class__.TYPES[typ]

    @classmethod
    def create(cls, control):
        ldtp_args = cls._ldtp_parse(control.character)
        if not ldtp_args: return None
        return cls(control.parent, *ldtp_args)

    def find(self):
        if not self.window.find(): return None
        cls = self.__class__
        elements = self.window.element.FindAll(DEF_SCOPE, self.condition)
        match_count = 0
        for i, ele in enumerate(elements):
            name_prop = cls.get_property(ele, 'Name')
            if name_prop == None: return None
            desc = cls._ldtp_desc(name_prop)
            if cls._wildcard_match(self.desc, desc):
                if match_count == self.index:
                    return ele
                match_count += 1
        return None

    @classmethod
    def get_property(cls, ele, prop):
        try:
            return ele.GetCurrentPropertyValue(_create_prop(prop))
        except ElementNotAvailableException:
            return None

    @classmethod
    def _ldtp_desc(cls, name):
        for ch in ['\r', '\n', '\t', ' ', '\xa0']:
            name = name.replace(ch, '')
        return name

    @classmethod
    def _ldtp_parse(cls, ldtp_str):
        if not isinstance(ldtp_str, str):
            return None
        typ = ldtp_str[0:3]
        if not typ in cls.TYPES:
            return None
        desc = ldtp_str[3:len(ldtp_str)]
        m = re.match(r'(.*?)([0-9]*)$', desc)
        if not m: return None
        desc = m.group(1)
        try:
            index = int(m.group(2))
        except ValueError:
            index = 0
        return typ, desc, index

    @classmethod
    def _wildcard_match(cls, ldtp_desc, control_desc):
        if ldtp_desc.find('*') == -1 and ldtp_desc.find('?')==-1:
            return ldtp_desc == control_desc
        ptn = ldtp_desc.replace('*', '.*').replace('?', '.')
        return re.match(ptn, control_desc)

def set_info(name, character, parent):
    try:
        if isinstance(character, str):
            character = character.decode('utf-8')
        else:
            for k in character:
                character[k] = character[k].decode('utf-8')
        controls[name] = Control(name, character, parent)
        set_info.no_info = False
        return True
    except:
        print sys.exc_info()[1]
set_info.no_info = True

def click(name, non_invoke=False):
    if non_invoke:
        return non_invoke_click(name)
    try:
        controls[name].get_pattern(InvokePattern).Invoke()
        return True
    except SystemError:
        print 'cannot invoke:', str(sys.exc_info()[1])
        return non_invoke_click(name)

def non_invoke_click(name):
    p = controls[name].find().GetClickablePoint()
    #rect = controls[name].get_property('BoundingRectangle')
    #print 'rect', rect.X, rect.Y, rect.Width, rect.Height
    #px = int(rect.X + rect.Width / 2)
    #py = int(rect.Y + rect.Height / 2)
    px, py = int(p.X), int(p.Y)
    ctypes.windll.user32.SetCursorPos(px, py)
    ctypes.windll.user32.mouse_event(MOUSEEVENT_LEFTDOWN, 0, 0, 0, 0)
    ctypes.windll.user32.mouse_event(MOUSEEVENT_LEFTUP, 0, 0, 0, 0)
    return True

def set_value(name, value):
    try:
        controls[name].get_pattern(ValuePattern).SetValue(value)
    except InvalidOperationException:
        sendkeys(name, '<ctrl>a' + value)
    return True

def exist(name):
    return controls[name].find(True) != None

def sendkeys(name, keys):
    keys = keys.decode('utf8')
    if name: activate(name)
    keys = _translate_keys(keys)
    SendKeys.SendWait(keys)
    return True

def activate(name):
    try:
        c = controls[name]
        if c.window:
            activate(c.window.name)
        else:
            handle = c.get_property('NativeWindowHandle')
            ctypes.windll.user32.SetForegroundWindow(handle)
        ele = c.find()
        ele.SetFocus()
    except SystemError:
        non_invoke_click(name)
    time.sleep(0.2)
    return True

def get_property(name, prop_name):
    return controls[name].get_property(prop_name)

def maximize(name):
    ptn = controls[name].get_pattern(WindowPattern)
    ptn.SetWindowVisualState(WindowVisualState.Maximized)
    return True

def value(name):
    return controls[name].value()

def close(name):
    ptn = controls[name].get_pattern(WindowPattern)
    ptn.Close()
    return True

def action(proc, control_name, args):
    try:
        return proc(control_name, *args)
    except ElementNotAvailableException:
        if exist(control_name):
            return proc(control_name, *args)
    return False

TRANS = {
    '<esc>': '{ESC}',
    '<tab>': '{TAB}',
    '<enter>': '~',
    '<up>': '{UP}',
    '<down>': '{DOWN}',
    '<home>': '{HOME}',
    '<pageup>': '{PGUP}',
    '<pagedown>': '{PGDN}',
    '<ctrl>': '^',
    '<alt>': '%',
    '<shift>': '+',
}
def _translate_keys(keys):
    for k in TRANS:
        to = TRANS[k]
        keys = keys.replace(k, to)
    return keys
