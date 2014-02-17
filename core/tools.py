try:
    import urllib.parse as parser
except ImportError:
    import urllib as parser

def is_channel(name):
    """Look at the prefix of `name` to determine whether its a channel or user"""
    prefixes = ['#', '&']
    if name and (name.lstrip()[0] in prefixes):
        return True
    return False

def quote_plus(url, fmt=None):
    """Quote illegal URL characters"""
    format = ':=()/?'
    if fmt:
        format += fmt
    return parser.quote_plus(url, format)
