#!/bin/bash
#
# Do any preproject setup needed before loading the StreamLab projects
#
# Assume we are running in the project directory
: ${HERE:=`dirname $0`}
echo SQLSTREAM_HOME=$SQLSTREAM_HOME
echo `whoami`
. /etc/bash.bashrc

DATADIR=/home/sqlstream/edr-data

mkdir /home/sqlstream/edr-data
cd $HERE
for f in *.lic
do
  cp -v $f $SQLSTREAM_HOME
done

nohup python ./test/generate_data.py -s $DATADIR/subscribers.csv -e $DATADIR/calldata.csv &  

echo ... data generation to file $DATADIR/calldata.csv started
cd -
