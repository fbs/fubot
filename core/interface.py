from zope.interface import Interface, Attribute

class IPlugin(Interface):
    """IPlugin baseclass"""
    name = Attribute("Name")
    version = Attribute("Version")
    author = Attribute("Author")

class IFinalize(IPlugin):
    """Interface for plugins that need to be finalized before unloading"""
    def finalize():
        """Called before the plugin gets unloaded"""
        pass

class IMsgHandler(IPlugin):
    """Interface for irc privmsgs filtered by command"""
    def accepts_command(cmd):
        """Return True if the plugin accepts command `cmd`, False otherwise"""
        pass

    def handle(proto, command, user, channel, args):
        """Handle a privmsg

        proto -- The protocol instance
        command -- The command issued
        user -- username in ['nick', 'realname', 'hostname'] format
        channel -- channel
        args -- The rest of the message as list"""
        pass

    def help(command):
        """Return a help string"""
        pass

    def list_commands():
        """Return a list of supported commands"""
        pass

class IRawMsgHandler(IPlugin):
    """Handle all privmsgs"""
    def handle(proto, user, channel, msg):
        """Handle a privmsg

        proto -- The protocol instance
        user -- username in ['nick', 'realname', 'hostname'] format
        args -- The message sent as list"""
        pass
