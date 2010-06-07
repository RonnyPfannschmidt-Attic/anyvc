"""
    anyvc
    ~~~~~~

    pythonic vcs abstractions

    :license: LPL2
    :copyright: Ronny Pfannschmidt and others
"""


from anyvc import apipkg
apipkg.initpkg(__name__,{
    'workdir':{
        'clone':'anyvc._workdir:clone',
        'checkout': 'anyvc._workdir:checkout',
        'open':'anyvc._workdir:open',
        },
    })
