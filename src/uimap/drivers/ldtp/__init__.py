try:
    import ldtp
except:
    import atomac.ldtp as ldtp
    import atomac
import uimap.wait as wait
import sys

class Driver():

    def __init__(self, uimap):
        pass

    def click(self, control):
        return ldtp.click(*_ldtp_args(control))

    def set_value(self, control, value):
        return ldtp.settextvalue(*_ldtp_args(control, value))

    def exist(self, control):
        if control.parent: self.renew(control.parent)
        return ldtp.guiexist(*_ldtp_args(control))

    def wait_exist(self, control):
        return wait.wait_exist(control)

    def sendkeys(self, control, keys):
        return ldtp.generatekeyevent(keys)

    def activate(self, control):
        return ldtp.activatewindow(*_ldtp_args(control))

    def renew(self, control):
        try:
            return ldtp.getobjectlist(*_ldtp_args(control))
        except ldtp.client_exception.LdtpExecutionError:
            return False

def _ldtp_args(control, *args):
    if control.parent:
        result = [control.parent.character]
    else:
        result = []
    return result + [control.character] + list(args)
