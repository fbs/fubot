from zope.interface import Interface, Attribute

class IPlugin(Interface):
    name = Attribute("Name")
    version = Attribute("Version")
    author = Attribute("Author")

class IInitialize(IPlugin):
    def initialize(conf):
        pass

class IFinalize(IPlugin):
    def finalize():
        pass

class IMsgHandler(IPlugin):
    def accepts_command(cmd):
        pass

    def handle(proto, user, channel, args):
        pass

class IRawMsgHandler(IPlugin):
    def handle(proto, user, channel, msg):
        pass
