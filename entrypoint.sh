#!/bin/bash
# Taken from sqlstream/complete:7.2.4 
# Remove final sleep

# trap ctrl-c and call ctrl_c()
trap ctrl_c INT

function ctrl_c() {
        echo "** Trapped CTRL-C"
}

if [ ! -z "$patching" ] 
   then 
   unattended-upgrade -d
fi


# If SQLSTREAM_JAVA_SECURITY_AUTH_LOGIN_CONFIG exist
#if [ ! -z "$SQLSTREAM_JAVA_SECURITY_AUTH_LOGIN_CONFIG" ] 
#   then  
#   echo "SQLSTREAM_JAVA_SECURITY_AUTH_LOGIN_CONFIG=$SQLSTREAM_JAVA_SECURITY_AUTH_LOGIN_CONFIG" >> /etc/sqlstream/environment 
#fi 

# If SQLSTREAM_JAVA_SECURITY_KRB5_CONF exist
#if [ ! -z "$SQLSTREAM_JAVA_SECURITY_KRB5_CONF" ]
#   then
#   echo "SQLSTREAM_JAVA_SECURITY_KRB5_CONF=$SQLSTREAM_JAVA_SECURITY_KRB5_CONF" >> /etc/sqlstream/environment 
#fi

source /etc/bash.bashrc
source /etc/sqlstream/environment
echo "Starting webagent..."
$SQLSTREAM_HOME/../clienttools/WebAgent/webagent.sh -a -w & echo $! > /var/run/sqlstream/webagentd.pid
echo "Starting s-Server..."
$SQLSTREAM_HOME/bin/s-Server &
echo "Starting s-Dashboard"
$SQLSTREAM_HOME/../s-Dashboard/s-dashboard.sh & echo $! > /var/run/sqlstream/s-dashboardd.pid
echo "Starting Kafka"
$SQLSTREAM_HOME/../services/startkafka.sh
$SQLSTREAM_HOME/../services/coverpaged start
source /etc/sqlstream/streamlab.environment
echo "Starting StreamLab"
$SQLSTREAM_HOME/streamlab.sh & echo $! > /var/run/sqlstream/streamlab.pid 
sudo service lighttpd start
sudo service postgresql start


