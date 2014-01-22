from zope.interface import Interface, Attribute

class IPlugin(Interface):
    name = Attribute("Name")
    version = Attribute("Version")

class IStart(IPlugin):
    def start():
        pass

class IStop(IPlugin):
    def stop():
        pass

class IMsgHandler(IPlugin):
    def handle(proto, user, channel, msg):
        pass
