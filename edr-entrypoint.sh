#!/bin/bash

HERE=$(dirname $0)

SQLSTREAM_JAVA_SECURITY_AUTH_LOGIN_CONFIG=
SQLSTREAM_JAVA_SECURITY_KRB5_CONF=

# run pre-startup steps

. $HERE/pre-startup.sh

# run the standard startup
. $HERE/entrypoint.sh

# run post-startup steps

# and sleep forever

. $HERE/sleep_forever.sh
