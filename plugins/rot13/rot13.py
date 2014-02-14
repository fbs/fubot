from zope.interface import implements

from core.interface import  IMsgHandler

def rotate(shift, line):
    """Rotate every alphabetic character in `line` by `shift` places"""
    line = line.lower()
    res = ''
    for char in line:
        if not char.isalpha():
            res += char
        else:
            num = ord(char) + shift
            if num > ord('z'):
                num = num % 123 + ord('a')
            res += chr(num)
    return res

class Rot13(object):
    """Simple Caesar Cipher implementation"""
    implements(IMsgHandler)

    name = 'rot13'
    version = '0.1'
    author = 'fbs'
    command = 'rot13'

    def accepts_command(self, cmd):
        """Test if `cmd` is an accepted command"""
        if cmd == self.command:
            return True
        return False

    def handle(self, proto, command, user, channel, args):
        """Handle an irc message"""
        user = user[0]

        if len(args) < 1:
            proto.msg(channel, '%s: Heh?' % user)
            return

        line = ' '.join(args[0:])
        rotated = rotate(13, line)
        print rotated
        proto.msg(channel, '%s: %s' % (user, rotated))

    def help(self, command):
        return 'Rot13 a string - %s <message>' % command

    def list_commands(self):
        return ['rot13']

def register():
    return Rot13()
