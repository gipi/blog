<!--
.. title: Init script per gunicorn e django
.. slug: init-script-per-gunicorn-e-django
.. date: 2011-06-19 00:00:00
.. tags: 
.. category: 
.. link: 
.. description: 
.. type: text
-->

.. code-block:: bash

 #!/bin/sh

 ### BEGIN INIT INFO
 # Provides:       seismic_web
 # Required-Start: $local_fs $syslog
 # Required-Stop:  $local_fs $syslog
 # Default-Start:  2 3 4 5
 # Default-Stop:   0 1 6
 # Short-Description: Gunicorn processes for seismic_web
 ### END INIT INFO

 # www-data is the default www user on debian
 USER=www-data
 #NAME="ktln2.org"
 NAME="t3st"
 RUN_DIR="/var/run/nginx/"
 # Confdir: the Django project inside the virtualenv
 CONFDIR="/var/www/${NAME}/"
 VENV_ACTIVATION=". env/bin/activate"

 RETVAL=0

 # PID: I always name my gunicorn pidfiles this way
 PID="${RUN_DIR}$NAME-gunicorn.pid"

 GUNICORN_RUN="gunicorn_django"

 GUNICORN_OPTS="--bind unix:${RUN_DIR}${NAME}-gunicorn.sock --daemon --pid=${PID}"
 # source function library
 . /lib/lsb/init-functions


 start()
 {
    echo "Starting $NAME."
    cd $CONFDIR;
    su -c "$VENV_ACTIVATION; $GUNICORN_RUN ${GUNICORN_OPTS} &" $USER && echo "OK" || echo "failed";
 }

 stop()
 {
    echo "Stopping $NAME"
    kill -QUIT `cat $PID` && echo "OK" || echo "failed";
 }

 reload()
 {
    echo "Reloading $NAME:"
    if [ -f $PID ]
    then kill -HUP `cat $PID` && echo "OK" || echo "failed";
    fi
 }

 case "$1" in
    start)
        start
        ;;
    stop)
        stop
        ;;
    restart)
        reload
        ;;
    reload)
        reload
        ;;
    force-reload)
        stop && start
        ;;
    *)
        echo $"Usage: $0 {start|stop|restart}"
        RETVAL=1
 esac
 exit $RETVAL