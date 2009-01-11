Workdir Operations
==================



.. class:: Workdir(path)

    :arg path: the base directory of the workdir
    :type path: str

    This is the basic interface of a Workdir
    vcs-related specials will be described separate.


    .. method:: add([paths][, recursive=False])

    .. method:: list([paths=()][, recursive=False])

    .. method:: commit([paths=()][,message])

        :keyword paths: paths to consider, its recursive on dirs
        :type paths: sequence or emtpy tuple
        :keyword message: commit message
        :type message: str

    .. method:: remove([paths])

    .. method:: revert([paths][, rev=None])

    .. method:: move(source, target)
        
        :type source: path or glob
        :type target: path or directory

    .. method:: diff([paths][, rev=None])
    
    .. method:: update([paths][, revision])



