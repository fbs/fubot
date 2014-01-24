from zope.interface import implements
from twisted.python import log

from core.interface import IPlugin, IMsgHandler
from core.pluginmanager import plugin_manager

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

    def handle(self, proto, user, channel, args):
        proto.msg(channel, '%s: pong' % user[0])

ping = Ping()
plugin_manager.register(ping)