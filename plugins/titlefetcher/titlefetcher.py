from twisted.web.client import getPage
from twisted.python import log
import re

from zope.interface import implements
from core.interface import IPlugin, IRawMsgHandler
from core.pluginmanager import plugin_manager

class TitleFetcher(object):
    implements(IRawMsgHandler)

    name = 'titlefetcher'
    version = '0.1'
    author = 'fbs'

    regex_url = re.compile(r"(?:^|\s)((?:https?://)?(?:[a-z0-9.\-]+[.][a-z]{2,4}/?)(?:[^\s()<>]*|\((?:[^\s()<>]+|(?:\([^\s()<>]+\)))*\))+(?:\((?:[^\s()<>]+|(?:\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:\'\".,<>?]))", flags=re.IGNORECASE|re.DOTALL)
    regex_title = re.compile(r'<title>(.*?)</title>', flags=re.IGNORECASE)

    def handle(self, proto, user, channel, msg):
        user = user[0]
        m = self.regex_url.search(msg)
        if m != None:
            log.msg("Url found: ", m.group(0))
            url = m.group(0)
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
