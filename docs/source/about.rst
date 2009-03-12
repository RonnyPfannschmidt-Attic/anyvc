==================
About
==================


Anyvc is a library to abstract common vcs operation.
It was born in an efford to enhance vcs operations in the pida ide.

The current version is mainly tailored to working with
the workingdirecties of the different vcs's and
performing operations like adding/renaming/moving files,
showing differences to the current commit and creating new commits.

Its still in the early stages of development,
but has already poven its practical value
in the versioncontrol service of pida.

Future versions will gradually expand the scope
from just workdirs to interacting with history
as well as managing repositories and branches.

Due to the differences in the vcs's
not all operations are availiable on all vcs's,
the abstraction will degrade/warn/error as it seems aporiate.


