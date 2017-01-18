#!/bin/sh
objectdir="/data/www/stttt2003pk_monitor_agent_cherry"
service_name="cherrypy_stttt2003pk_monitor.service"
runfile="run.py"
count=0

/usr/bin/inotifywait -mrq --exclude "(data|tmp|\.git|cherrypy_pid.pid|static|logs|shell|\.swp|\.swx|\.pyc|\.py\~)" --timefmt '%d/%m/%y %H:%M' --format '%T %w%f' --event modify,delete,move,create,attrib ${objectdir} |  while read files;
do
    systemctl restart supervisord.service;
    echo $files >> /var/log/test_autoreload.log;
done &
