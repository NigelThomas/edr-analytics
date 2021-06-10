#!/bin/bash
# Derived from drs

IMAGE=$1
CONTAINER=sqlstream

shift

PORTS="-p 5560:5560 -p 5570:5570 -p 5580:5580"
SL_PORTS="-p 5585:5585 -p 5590:5590 -p 5595:5595"

if [[ $IMAGE =~ complete ]]
then
    PORTS="-p 80:80 $PORTS $SL_PORTS"
elif [[ $IMAGE =~ streamlab ]]
then
    PORTS="-p 5590:80"
    CONTAINER=streamlab
elif [[ $IMAGE =~ coverpage ]]
then
    PORTS="-p 80:80"
    CONTAINER=coverpage
elif [[ $IMAGE =~ dashboard ]]
then
    PORTS="-p 5595:80"
    CONTAINER=s-dashboard
elif [[ $IMAGE =~ rose ]]
then
    PORTS="-p 5585:80"
    CONTAINER=rose
elif [[ $IMAGE =~ s-server ]]
then
    # default ports only
    PORTS="$PORTS"
fi

if [ -z "$IMAGE" ]
then
   echo "No image provided"
else
   if [[ $IMAGE =~ ^[a-z]+\:[7-9]\.[0-9]\.[0-9]\.[0-9|a-f|\-]+$ ]]
   then
      # assume we want to run images from thales gitlab
      IMAGE="gitlab.thalesdigital.io:5005/guavus/sqlstream/devops/sqlstream-devops/$IMAGE"
   fi

   docker kill $CONTAINER
   docker rm $CONTAINER

   echo "Running image $IMAGE ports $PORTS as container $CONTAINER"
   docker run -v $(pwd):/home/sqlstream/app --entrypoint /home/sqlstream/app/edr-entrypoint.sh $PORTS -d --name $CONTAINER $* -it $IMAGE

fi
