#!/bin/bash

########################################################################################################################
# Create ZIP package of the plugin ready for upload to plugin repository
########################################################################################################################

set -u # Exit if we try to use an uninitialised variable
set -e # Return early if any command returns a non-0 exit status

echo "CREATE PLUGIN"

command -v zip >/dev/null 2>&1 || { echo "I require zip but it's not installed.  Aborting." >&2; exit 1; }

PWD=`pwd`
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PLUGIN=landxmlconvertor
SRC=$DIR/../$PLUGIN
DEST="$DIR/../build"
DEST_BUILD=$DEST/$PLUGIN

if [ ! -d "$SRC" ]; then
  echo "Missing directory $SRC"
  exit 1
fi

rm -rf $DEST_BUILD
mkdir -p $DEST_BUILD

cp -R $SRC/* $DEST_BUILD/
find $DEST_BUILD -type l -exec unlink {} \;

find $DEST_BUILD -name \*.pyc -delete
find $DEST_BUILD -name __pycache__ -delete

cd $DEST_BUILD/..

if [ -f "$DEST/$PLUGIN.zip" ]; then
    rm $DEST/$PLUGIN.zip
fi

zip -r $DEST/$PLUGIN.zip $PLUGIN --exclude *.idea*

echo "$DEST/$PLUGIN.zip created"

cd $PWD
