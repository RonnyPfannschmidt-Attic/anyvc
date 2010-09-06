VCS Abstraction Backends
=========================


currently anyvc ships with support for


.. tableofcontents::


Mercurial
---------

The Mercurial backend is implemented in Terms of the basic merucrial api.
It does not support extension discovery or extensions.


Git
----

The Git backend is split.
Workdir support is implemented in terms of the git CLI because Dulwich has no complete support.
Repository support is implemented in terms of Dulwich, cause its supported and the better 'api'.


Bazaar
-------

The Bazaar backend is implemented in terms of bzrlib.
It is to be considered as 'passes the tests' not as first class citizen


Subversion
-----------

The Subversion backend is split as well.
The workdir part is implemented in terms of the cli,
because the subversion checkout api requires complicated locking patterns.
The Repository support is implemented in terms of subvertpy.
