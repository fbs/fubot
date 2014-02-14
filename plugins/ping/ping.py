from zope.interface import implements
from twisted.python import log

from core.interface import IMsgHandler


class Ping():
    implements(IMsgHandler)

    name = 'ping'
    version = '0.1'
    author = 'fbs'
    command = 'ping'

    def accepts_command(self, cmd):
        if cmd == self.command:
            return True
        return False

    def handle(self, proto, command, user, channel, args):
        proto.msg(channel, '%s: pong' % user[0])

    def help(self, command):
        return 'Pongs you'

    def list_commands(self):
        return ['ping']

def register():
    return Ping()
