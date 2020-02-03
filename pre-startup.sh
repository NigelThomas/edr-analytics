#!/bin/bash
#
# Do any preproject setup needed before loading the StreamLab projects
#
# Assume we are running in the project directory
echo SQLSTREAM_HOME=$SQLSTREAM_HOME
echo `whoami`

mkdir /home/sqlstream/edr-data
nohup python ./generate_data.py >/home/sqlstream/edr-data/calldata.csv &

echo ... data generation to file started



