#!/bin/sh

# Abort on error
set -e

# Replace environment variables in the configuration file
envsubst < /etc/nginx/default.conf.tpl > /etc/nginx/conf.d/default.conf
# Start Nginx. Daemon off means it will run ngnix in the foreground.
# This will make sure that nginx will be the primary process of the container.
# And all logs will be displayed. Once the nginx process is stopped, the container will stop.
nginx -g 'daemon off;'