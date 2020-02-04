#!/bin/bash
#
# Do any preproject setup needed before loading the StreamLab projects
#
# Assume we are running in the project directory
echo SQLSTREAM_HOME=$SQLSTREAM_HOME
echo `whoami`
DATADIR=/home/sqlstream/edr-data

mkdir /home/sqlstream/edr-data
nohup python test/generate_data.py -s $DATADIR/subscribers.csv -e $DATADIR/calldata.csv &  

echo ... data generation to file started



