# copyright 2008 by Ronny Pfannschmidt
# license lgpl3 or later
"""
>>> StatedPath('a').abspath
>>> StatedPath('a', base='b').abspath
'b/a'
>>> StatedPath('a')
<normal 'a'>
>>> StatedPath('./a')
<normal 'a'>
"""
from anyvc.workdir.file import StatedPath

