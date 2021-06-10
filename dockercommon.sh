#!/bin/bash
#
# start a development container, load all slab files from the current project

: ${CONTAINER_NAME:=sqlstream/complete}

# kill any edr test container running on this host (because ports will clash)
# TODO only kill those that are actually running

docker kill $CONTAINER_NAME

docker rm $CONTAINER_NAME

# Unless disabled, link the target volume

#if [ "$HOST_DATA_TARGET" = "none" ]
#then
#    HOST_TGT_MOUNT=
#else
#    HOST_TGT_MOUNT="-v ${HOST_DATA_TARGET:=$HOME/orctest-output}:$CONTAINER_DATA_TARGET"
#fi

# note: you may use the project's own jndi directory in which case working copies of properties files will override committed/pushed copies

#if [ -n "$HOST_JNDI_DIR" ]
#then
#    HOST_JNDI_MOUNT="-v ${HOST_JNDI_DIR:=$HERE/jndi}:$CONTAINER_JNDI_DIR"
#fi

#docker run -v ${HOST_DATA_SOURCE:=$HOME/vzw/iot}:$CONTAINER_DATA_SOURCE $HOST_TGT_MOUNT $HOST_JNDI_MOUNT \

docker run \
           -p 80:80 -p 5560:5560 -p 5580:5580 -p 5585:5585 -p 5590:5590 \
           -v $(pwd):/home/sqlstream/app \
           -e LOAD_SLAB_FILES="${LOAD_SLAB_FILES:=edr*.slab}" \
           -e SQLSTREAM_HEAP_MEMORY=${SQLSTREAM_HEAP_MEMORY:=4096m} \
           -e SQLSTREAM_SLEEP_SECS=${SQLSTREAM_SLEEP_SECS:=10} \
           -d --rm --name $CONTAINER_NAME -it $BASE_IMAGE:${BASE_IMAGE_LABEL:=latest}

docker logs -f $CONTAINER_NAME
