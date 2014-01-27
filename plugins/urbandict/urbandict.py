from zope.interface import implements
from twisted.web.client import getPage
from twisted.python import log
from twisted.web import error as web_error
from twisted.internet import error as internet_error

import re
import json

try:
    import urllib.parse as parser
except ImportError:
    import urllib as parser

from core.interface import IPlugin, IMsgHandler
from core.pluginmanager import plugin_manager

def _make_apiurl(query):
    APIURL = 'http://api.urbandictionary.com/v0/define?term=%s'
    return parser.quote_plus(APIURL % query, ':=()/?')

def _make_weburl(query):
    WEBURL = 'http://www.urbandictionary.com/define.php?term=%s'
    return parser.quote_plus(WEBURL % query, ':=()/?')

# Stolen from somewhere
def _repairjson(original):
    original = original.replace(r'\r','').replace(r'\n','')
    original = original.replace('\\x', '\\u00')
    regex = re.compile(r'\\(?![/u"])')
    fixed = regex.sub(r"\\\\", original)
    return fixed


class Urban(object):
    implements(IMsgHandler)

    name = 'urbandict'
    version = '0.1'
    author = 'fbs'
    command = 'urban'

    def accepts_command(self, cmd):
        if cmd == self.command:
            return True
        return False

    def handle(self, proto, command, user, channel, args):
        user = user[0]
        self.query  = ' '.join(args)
        self.weburl = _make_weburl(self.query)
        self.apiurl = _make_apiurl(self.query)

        d = getPage(self.apiurl)
        d.addCallback(self.handle_page, proto, user, channel)
        d.addCallback(self.search_page, proto, user, channel)
        d.addErrback(self.errback, proto, user, channel)

    def handle_page(self, page, proto, user, channel):
        jsondata = _repairjson(page.decode('utf-8'))
        jsondata = json.loads(jsondata)
        return jsondata

    def search_page(self, page, proto, user, channel):
        results = page.get('result_type')
        definitions = page.get('list')

        if results == 'exact':
            output = definitions[0]['definition'].encode('ascii').strip()
            log.msg(self.weburl)
            proto.msg(channel, '%s: %s, see %s for more.' %
                      (user, output, self.weburl))
        else:
            proto.msg(channel, '%s: Sorry, no results found' % user)


    def errback(self, failure, proto, user, channel):
        log.err('Plugin: %s: type: %s | message: %s' %
                (self.name, failure.type, failure.getErrorMessage()))

        r = failure.check(web_error.Error,
                         internet_error.ConnectError,
                         ValueError)
        if r == ValueError:
            proto.msg(channel, '%s: Urban: Couldn\'t decode the JSON, sorry :(' % user)
        elif r == web_error.Error:
            proto.msg(channel,  '%s: Urban: Couldn\'t fetch the page, sorry :(' % user)
        elif r == internet_error.ConnectError:
            proto.msg(channel, '%s: Urban: Couldn\'t connect to the server, sorry :(' % user)

    def help(self, command):
        return 'Lookup a term on urban dictionary - %s <term>' % command
        pass

    def list_commands(self):
        return ['urban']

urban = Urban()
plugin_manager.register(urban)
