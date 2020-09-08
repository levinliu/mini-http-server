#!/bin/sh

if [ ! -e ".venv" ] ; then
    #create virtualenv with default option
    virtualenv .venv
fi

ps -ef|grep 'server.py' |grep -v grep|awk -F" " '{print $2}' | while read PID
do
    echo "kill existing pid ${PID}"
    kill -9 "${PID}"
done
# activate python2 context and start server
source .venv/bin/activate && python server.py & 
