#!/bin/bash

NAME="themenu"                                  # Name of the application
DJANGODIR=/var/git/themenu
USER=goober                                        # the user to run as
NUM_WORKERS=3                                     # how many worker processes should Gunicorn spawn
DJANGO_SETTINGS_MODULE=themenu.settings             # which settings file should Django use
DJANGO_WSGI_MODULE=themenu.wsgi                     # WSGI module name

echo "Starting $NAME as `whoami`"

# Activate the virtual environment
cd $DJANGODIR
source /home/${USER}/${NAME}/bin/activate


# Start your Django Unicorn
# Programs meant to be run under supervisor should not daemonize themselves (do not use --daemon)

exec gunicorn ${DJANGO_WSGI_MODULE}:application \
  --bind "127.0.0.1:8000"
  --name $NAME \
  --workers $NUM_WORKERS \
  --log-level=debug \
  --log-file=-

