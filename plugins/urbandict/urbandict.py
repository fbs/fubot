from zope.interface import implements
from twisted.web.client import getPage
from twisted.python import log

import re
import json

try:
    import urllib.parse as parser
except ImportError:
    import urllib as parser

from core.interface import IPlugin, IMsgHandler
from core.pluginmanager import plugin_manager

class Urban(object):
    implements(IMsgHandler)

    name = 'urbandict'
    version = '0.1'
    author = 'fbs'
    command = 'urban'
    BASEURL = 'http://api.urbandictionary.com/v0/define?term=%s'

    def accepts_command(self, cmd):
        if cmd == self.command:
            return True
        return False

    def _repairjson(self, original):
        original = original.replace(r'\r','').replace(r'\n','')
        original = original.replace('\\x', '\\u00')
        regex = re.compile(r'\\(?![/u"])')
        fixed = regex.sub(r"\\\\", original)
        return fixed

    def handle(self, proto, user, channel, args):
        user = user[0]
        url = self.BASEURL % (''.join(args))
        url = parser.quote_plus(url, ':=()/?')
        d = getPage(url)

        d.addCallback(self.parse_json, proto, user, channel)
        d.addErrback(self.fetch_failed, proto, user, channel)
        d.addCallback(self.send_definition, proto, user, channel)
        d.addErrback(self.send_definition_failed, proto, user, channel)

    def parse_json(self, page, proto, user, channel):
        jsondata = self._repairjson(page.decode('utf-8'))
        jsondata = json.loads(jsondata)
        return jsondata

    def send_definition(self, page, proto, user, channel):
        results = page.get('result_type')
        definitions = page.get('list')

        if results == 'exact':
            output = definitions[0]['definition'].encode('ascii').strip()
        else:
            output = "No results found"

        proto.msg(channel, "%s: %s" % (user, output))


    def parse_json_failed(self, failure, proto, user, channel):
        proto.msg(channel, '%s: failed to parse JSON data' % user)
        log.msg('Failed to parse json' % failure)

    def send_definition_failed(self, failure, proto, user, channel):
        proto.msg(channel, '%s: failed to find definitions' % user)
        log.msg('Failed to find definitions ', failure)

    def fetch_failed(self, failure, proto, user, channel):
        proto.msg(channel, '%s: Couldn\'t fetch json' % user)
        log.msg("Failed to fetch urban json: ", failure)

urban = Urban()
plugin_manager.register(urban)
