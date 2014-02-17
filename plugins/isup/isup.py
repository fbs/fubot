from zope.interface import implements
from twisted.web.client import getPage
from twisted.python import log
from twisted.web import error as web_error
from twisted.internet import error as internet_error

from bs4 import BeautifulSoup

from core.interface import IMsgHandler
from core.tools import quote_plus

URL = 'http://www.isup.me/%s'

class IsUp():
    """Use isup.me to test if sites are up or down"""
    implements(IMsgHandler)
    name = 'isup'
    version = '0.1'
    author = 'fbs'
    command = 'isup'
    commands = ['isup', 'isdown']

    def help(self, command):
        """Print help"""
        return 'Test if a site is up or down  - usage: %s <url>' % command

    def list_commands(self):
        """Return a list of accepted commands"""
        return self.commands

    def accepts_command(self, cmd):
        """Test if command is accepted"""
        return cmd in self.commands

    def handle(self, proto, command, user, channel, args):
        """Entry point for command handling"""
        user = user[0]

        if len(args) == 0:
            proto.msg(channel, '%s: Which site do you want me to check?' % user)
            return

        target_url = ' '.join(args).strip()
        isupurl = quote_plus(URL % target_url)

        d = getPage(isupurl)
        d.addCallback(self.cbSearchpage, proto, user, channel, target_url)
        d.addErrback(self.ebFailure, proto, user, channel)

    def ebFailure(self, failure, proto, user, channel):
        """The ErrBack that handles failures"""
        log.err('Plugin: %s: type: %s | message: %s' %
                (self.name, failure.type, failure.getErrorMessage()))

        r = failure.check(web_error.Error, internet_error.ConnectError)

        if r == web_error.Error or r == internet_error.ConnectError:
            proto.msg(channel, user + ': [isup] isup.me seems down :/')
        else:
            proto.msg(channel, user + ': [isup] Something failed, but i dont ' +
                      'know what :/')

    def cbSearchpage(self, page, proto, user, channel, url):
        """Callback on successful page fetch"""
        soup = BeautifulSoup(page)
        if "It's not just you" in soup.div.text:
            proto.msg(channel, '%s: %s seems to be down' % (user, url))
        else:
            proto.msg(channel, '%s: %s seems up.' % (user, url))

def register():
    """Function to be called by the plugin manager"""
    return IsUp()
