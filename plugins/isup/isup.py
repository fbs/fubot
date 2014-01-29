from zope.interface import implements
from twisted.web.client import getPage
from twisted.python import log
from twisted.web import error as web_error
from twisted.internet import error as internet_error

from bs4 import BeautifulSoup

from core.interface import IMsgHandler

try:
    import urllib.parse as parser
except ImportError:
    import urllib as parser

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
        return 'Test if a site is up or down  - usage: %s <url>' % command
        pass

    def list_commands(self):
        return self.commands

    def accepts_command(self, cmd):
        return cmd in self.commands

    def handle(self, proto, command, user, channel, args):
        user = user[0]

        target_url = ' '.join(args).strip()
        isupurl = parser.quote_plus(URL % target_url, ':=()/?')

        d = getPage(isupurl)
        d.addCallback(self.cbSearchpage, proto, user, channel, target_url)
        d.addErrback(self.ebFailure, proto, user, channel)

    def ebFailure(self, failure, proto, user, channel):
        log.err('Plugin: %s: type: %s | message: %s' %
                (self.name, failure.type, failure.getErrorMessage()))

        r = failure.check(web_error.Error, internet_error.ConnectError)

        if r == web_error.Error or r == internet_error.ConnectError:
            proto.msg(channel, '%s: isup.me seems down :/' % user)
        else:
            proto.msg(channel, '%s: Something failed, but i dont know what :/'
                      % user)

    def cbSearchpage(self, page, proto, user, channel, url):
        soup = BeautifulSoup(page)
        if "It's not just you" in soup.div.text:
            proto.msg(channel, '%s: %s seems to be down' % (user, url))
        else:
            proto.msg(channel, '%s: %s seems up.' % (user, url))

def register():
    return IsUp()
