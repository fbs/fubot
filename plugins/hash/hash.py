from zope.interface import implements
from twisted.python import log

from core.interface import IPlugin, IMsgHandler
from core.pluginmanager import plugin_manager

import hashlib

class Hash(object):
    implements(IMsgHandler)

    name = 'hash'
    version = '0.1'
    author = 'fbs'
    command = 'hash'

    def accepts_command(self, cmd):
        if cmd == self.command:
            return True
        return False

    def handle(self, proto, user, channel, args):
        user = user[0]
        if len(args) == 0:
            proto.msg(channel, '%s: Supported algorithms: %s' %
                      (user, ' '.join(hashlib.algorithms)))
            return
        if len(args) < 2:
            proto.msg(channel, '%s: Not enough arguments' % user)
            return
        method = args[0].lower()
        str = ' '.join(args[1:])

        try:
            h = hashlib.new(method)
        except ValueError:
            proto.msg(channel, '%s: Algorithm not supported: use one of [%s]' %
                      (user, ' '.join(hashlib.algorithms)))
            return
        h.update(str)
        proto.msg(channel, '%s: %s' % (user, h.hexdigest()))


hash = Hash()
plugin_manager.register(hash)
