def is_channel(name):
    """Look at the prefix of `name` to determine whether
    its a channel or user"""
    prefixes = ['#', '&']
    if name and (name.lstrip()[0] in prefixes):
        return True
    return False
