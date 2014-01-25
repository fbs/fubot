from zope.interface import implements
from twisted.python import log

from core.interface import IPlugin, IMsgHandler
from core.pluginmanager import plugin_manager

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

    def handle(self, proto, user, channel, args):
        if not self.is_owner(user):
            proto.msg(channel, '%s: You\'re not my owner :o' % user[0])
            log.msg('%s tried to execute admin commands' % user)

        if len(args) < 1:
            proto.msg(channel, '%s: No arguments..?' % user[0])
            return

        cmd = args[0]
        args = ' '.join(args[1:])

        if cmd == 'quit':
            proto.bot.quit()
            return

        if cmd == 'load':
            plugin_manager.load(args)
            return

        if cmd == 'reload':
            plugin_manager.reload(args)
            return

        if cmd == 'reload_all':
            plugin_manager.reload_all()
            return

admin = Admin()
plugin_manager.register(admin)
