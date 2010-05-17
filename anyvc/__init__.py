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
        'all_known':'anyvc._workdir:all_known',
        'get_workdir_manager_for_path':'anyvc._workdir:get_workdir_manager_for_path',
        'open':'anyvc._workdir:open',
        },
    })
