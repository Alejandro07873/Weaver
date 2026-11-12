"""Asset-reference helper used by the project inspector."""
import re


def object_reference(value):
    name = value.get('ObjectName', '')
    path = value.get('ObjectPath', '')
    if not name or not path:
        return 'None'
    kind, _, tail = name.partition("'")
    object_name = tail.rstrip("'").split('.')[-1]
    path = re.sub(r'\.\d+$', '', path)
    if '/Content/' in path:
        path = '/Game/' + path.split('/Content/', 1)[1]
    if not path.startswith('/'):
        raise ValueError(f'Unresolved asset path: {path}')
    package = path.split('.')[0]
    return f"{kind}'{package}.{object_name}'"
