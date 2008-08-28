"""
>>> StatedPath('a').abspath
>>> StatedPath('a', base='b').abspath
'b/a'
>>> StatedPath('a')
<normal 'a'>
"""
from anyvc.file import StatedPath

