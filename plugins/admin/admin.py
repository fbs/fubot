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

    def help(self, command):
        return 'Can\'t help you on this'

    def list_commands(self):
        return ['admin']

    def handle(self, proto, command, user, channel, args):
        if not self.is_owner(user):
            proto.msg(channel, '%s: You\'re not my owner :o' % user[0])
            log.msg('%s tried to execute admin commands' % user)

        if len(args) < 1:
            proto.msg(channel, '%s: No arguments..?' % user[0])
            return

        cmd = args[0]
        args = args[1:]

        log.msg('Admin Command [%s]' % cmd)
        if cmd == 'quit':
            proto.bot.quit()
            return

        if cmd == 'load':
            for arg in args:
                plugin_manager.load(arg)
            return

        if cmd == 'unload':
            for arg in args:
                plugin_manager.unload(arg)
            return

        if cmd == 'reload':
            for arg in args:
                plugin_manager.reload(arg)
            return

        if cmd == 'reload_all':
            plugin_manager.reload_all()
            return

        if cmd == 'list':
            #FIXME
            plugins = plugin_manager.plugins
            line = ''
            for name in plugins:
                line += name + ' '
            proto.msg(channel, '%s: %s' % (user[0], line))

admin = Admin()
plugin_manager.register(admin)
