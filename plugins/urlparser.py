from twisted.web.client import getPage
import re

from zope.interface import implements
from core.interface import IPlugin, IMsgHandler
from core.pluginmanager import plugin_manager

class URLParser(object):
    implements(IMsgHandler)

    regex_url = re.compile(r'\bhttps?://\S+')
    regex_title = re.compile(r'<title>(.*?)</title>', flags=re.IGNORECASE)

    def handle(self, fubot, user, channel, msg):
        m = self.regex_url.search(msg)
        if m != None:
            url = m.group(0)
            getPage(url).addCallback(self.send_title, fubot, user, channel)

    def send_title(self, page, fubot, user, channel):
        iter = self.regex_title.finditer(page)
        try:
            title = iter.next().groups()
            fubot.msg(channel, 'title: %s' % title[0])
        except StopIteration:
            pass

urlparser = URLParser()
plugin_manager.register(urlparser)
