from zope.interface import implements
from twisted.python import log

from core.interface import IMsgHandler

class Admin(object):
    implements(IMsgHandler)

    name = 'admin'
    version = '0.1'
    author = 'fbs'
    command = 'admin'

    trusted_vhost = ['127.0.0.1']

    def is_owner(self, user):
        if user[2] in self.trusted_vhost:
            return True
        return False

    def accepts_command(self, cmd):
        if cmd == self.command:
            return True
        return False

    def help(self, command):
        return 'Can\'t help you on this'

    def list_commands(self):
        return ['admin']

    def handle(self, proto, command, user, channel, args):
        if not self.is_owner(user):
            proto.msg(channel, '%s: You\'re not my owner :o' % user[0])
            log.msg('%s tried to execute admin commands' % user)
            return

        if len(args) < 1:
            proto.msg(channel, '%s: No arguments..?' % user[0])
            return

        cmd = args[0]
        args = args[1:]

        log.msg('Admin Command [%s]' % cmd)
        if cmd == 'quit':
            return

        if cmd == 'load':
            return

        if cmd == 'unload':
            return

        if cmd == 'reload':
            return

        if cmd == 'reload_all':
            return

        if cmd == 'list':
            return

def register():
    return Admin()
