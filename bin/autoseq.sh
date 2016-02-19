#!/usr/bin/env bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
JARS="$DIR/../../autoseq/lib/*:$DIR/../../autoseq/target/scala-2.10/*"
MAINCLASS="org.broadinstitute.gatk.queue.QCommandLine"

java -cp $JARS -Dscala.usejavacp=true $MAINCLASS "$@"

