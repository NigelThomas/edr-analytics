#!/bin/bash
#
# start a development container, load all slab files from the current project

HERE=$(cd `dirname $0`; pwd)
BASE_IMAGE=sqlstream/streamlab-git-dev
BASE_IMAGE_LABEL=release
CONTAINER_NAME=edr_dev

: ${LOAD_SLAB_FILES:=edr.slab}


. $HERE/dockercommon.sh

