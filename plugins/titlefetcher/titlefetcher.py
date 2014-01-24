from twisted.web.client import getPage
from twisted.python import log
import re
import iptools
import urlparse
from zope.interface import implements
from core.interface import IPlugin, IRawMsgHandler
from core.pluginmanager import plugin_manager

INTERNAL_IPS = iptools.IpRangeList(
    '127/8',
    '192.168/16',
    '10/8',
    '::1',
    'fe80::/10',
    'fc00::/7'
)

def acceptable_netloc(hostname):
    ok = True
    try:
        if hostname in INTERNAL_IPS:
            ok = False
    except TypeError:
        if hostname == 'localhost':
            ok = False
    return ok

class TitleFetcher(object):
    implements(IRawMsgHandler)

    name = 'titlefetcher'
    version = '0.1'
    author = 'fbs'

    regex_url = re.compile(r"(?i)\b((?:[a-z][\w-]+:(?:/{1,3}|[a-z0-9%])|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:\'\".,<>?]))", flags=re.IGNORECASE)

    regex_title = re.compile(r'<title>(.*?)</title>', flags=re.IGNORECASE)

    def handle(self, proto, user, channel, msg):
        user = user[0]
        m = self.regex_url.search(msg)
        if m != None:
            url = m.group(0)
            if not acceptable_netloc(urlparse.urlparse(url).netloc):
                proto.msg(channel, '%s: Thats an invalid netloc you badboy'
                          % user)
                return

            if url[:7].lower() != "http://" and url[:8].lower() != "https://":
                url = "http://" + url
            d = getPage(url).addCallback(self.send_title, proto, user, channel)
            # No errbacks, dont want to flood chat with crap

    def send_title(self, page, proto, user, channel):
        iter = self.regex_title.finditer(page)
        try:
            title = iter.next().groups()[0]
            log.msg("Title: ", title, 'Channel ', channel)
            proto.msg(channel, 'title: %s' % title)
        except StopIteration:
            pass

o = TitleFetcher()
plugin_manager.register(o)
