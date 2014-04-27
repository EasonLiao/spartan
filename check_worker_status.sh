#!/bin/bash

cat worker.cnf | while read LINE
do
    ip=`echo "$LINE" | awk '{print $1}'`
    host=$ip
    
    echo "Checking server $host..."
    ssh $host $" ps aux | pgrep python >/dev/null && echo 'Name | CPU usage %: ' &&  ps aux | \
      grep python | grep spartan | grep -v grep | grep -v bash |  awk '{print \$11; print \$3}' \
      || echo 'no process found!'" &
    sleep 0.1 

done

wait
