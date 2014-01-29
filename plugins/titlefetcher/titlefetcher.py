from twisted.web.client import getPage
from twisted.python import log
import re
import iptools
import urlparse
from bs4 import BeautifulSoup

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

REGEX_URL = re.compile(r"(?i)\b((?:[a-z][\w-]+:(?:/{1,3}|[a-z0-9%])|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:\'\".,<>?]))", flags=re.IGNORECASE)

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

    # Thanks to cardinal https://github.com/JohnMaguire2013/Cardinal
    def handle(self, proto, user, channel, msg):
        user = user[0]
        m = REGEX_URL.search(msg)
        if m != None:
            url = m.group(0)
            if not acceptable_netloc(urlparse.urlparse(url).netloc):
                proto.msg(channel, '%s: Thats an invalid netloc you badboy'
                          % user)
                return

            if url[:7].lower() != "http://" and url[:8].lower() != "https://":
                url = "http://" + url

            log.msg('Url found [%s]' % url)
            d = getPage(url)
            d.addCallback(self.send_title, proto, user, channel)
            d.addErrback(self.errback)
            # No errbacks, dont want to flood chat with crap

    def errback(self, failure):
        log.err('[Titlefetcher] %s' % failure.getErrorMessage())

    def send_title(self, page, proto, user, channel):
        """Callback that searches page `page` for a title and sends it to
        the channel if found"""
        soup = BeautifulSoup(page)
        title = soup.title.string.strip().encode('ascii')
        proto.msg(channel, 'title: %s' % title)


o = TitleFetcher()
plugin_manager.register(o)
