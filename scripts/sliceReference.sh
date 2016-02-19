#!/usr/bin/env bash

set -eo pipefail

COMMIT=`git rev-parse --short HEAD`
COMMITDATE=`git show -s --format=%ci $COMMIT`
VERSION=`grep version autoseq/build.sbt | perl -nle 's/\"(.+)\"//; print $1'`

echo
echo "Starting autoseqer version $VERSION ($COMMIT/$COMMITDATE)"
echo

#Initialize PyEnv
export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init -)"

#Initialize CPANminus
eval `perl -I ~/perl5/lib/perl5 -Mlocal::lib`

## Set python version for this shell only (and it's spawned shells or Queue jobs)
pyenv shell 2.7.8

QUEUEJAR=./autoseq/lib/Queue.jar
YAMLJAR=./autoseq/lib/snakeyaml-1.14.jar

java -cp $YAMLJAR:$QUEUEJAR:target/scala-2.10/* -Dscala.usejavacp=true org.broadinstitute.gatk.queue.QCommandLine "$@"

echo
echo
echo "AutoSeqer Reference Genome Generator done."
exit 0
