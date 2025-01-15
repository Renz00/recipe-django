#!bin/sh

# Abort immediately on any errors
set -e

python manage.py wait_for_db
# Collect all static files and place them in the configured
# static file directory
python manage.py collectstatic --noinput
python manage.py migrate

# Start the uWSGI server on port 9000
uswgi --socket :9000 --workers 4 --master --enable-threads --module app.wsgi