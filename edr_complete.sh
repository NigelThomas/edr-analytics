#!/bin/bash
#
# start a development container, load all slab files from the current project

HERE=$(cd `dirname $0`; pwd)
BASE_IMAGE=sqlstream/complete
BASE_IMAGE_LABEL=latest
CONTAINER_NAME=sqlstream

: ${LOAD_SLAB_FILES:=*.slab}


. $HERE/dockercommon.sh

