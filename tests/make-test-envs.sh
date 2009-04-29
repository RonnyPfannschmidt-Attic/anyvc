#!/usr/bin/bash

VCS=(hg bzr svn)

PACKAGE_hg="mercurial"
PACKAGE_bzr="bzr"
PACKAGE_svn="subvertpy"

VERSION_bzr=$(echo 1.{6..14})
VERSION_mercurial="1.0 1.1 1.2 1.2.1"
VERSION_subvertpy=$(echo 0.6.{0..5})

for vc in ${VCS[@]}
do
    echo VC $vc

    package_ref="PACKAGE_${vc}"
    package="${!package_ref}"
    vref="VERSION_${package}"
    versions=${!vref}

    mkdir -p virtualenvs/$vc
    pushd virtualenvs/$vc

    for version in $versions
    do
        if [[ ! -d $version ]]
        then 
            echo "installing" $package==$version
            virtualenv -q $version
            ./$version/bin/easy_install -q $package==$version
        fi
    done
    popd # virtualenvs/$vc
done
