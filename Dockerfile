FROM python:3.9-alpine3.13
LABEL maintainer="renz00"

# this is recommended when developing with python in a containers
# this will prevent any delays with terminal logs
ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt /tmp/requirements.txt
COPY ./requirements.dev.txt /tmp/requirements.dev.txt
COPY ./app /app
WORKDIR /app
EXPOSE 8000

# by default DEV is false. When docker compose is used, the DEV variable will be overwritten to true
ARG DEV=false
    # create a virtual environment
RUN python -m venv /py && \
    # upgrade pip to latest version
    /py/bin/pip install --upgrade pip && \
    # install the postgresql driver and all needed dependencies into alpine image
    apk add --update --no-cache postgresql-client && \
    # groups all dependencies into tmp-build-deps for easier management. 
    # postgresql-client is not included since it is not needed to be removed later.
    apk add --update --no-cache --virtual .tmp-build-deps \
        build-base postgresql-dev musl-dev && \
    # install all dependencies in the requirements.txt file
    /py/bin/pip install -r /tmp/requirements.txt && \
    # shell script that will check if dev dependencies should be installed
    if [ $DEV = "true" ]; \
        then /py/bin/pip install -r /tmp/requirements.dev.txt ; \
    fi && \
    # remove the tmp directory containing the requirements files
    rm -rf /tmp && \
    # remove the depenencies used to install postgresql driver
    apk del .tmp-build-deps && \
    # add a user to the alpine image to manage the application
    adduser \
        # disable logins and use the user as default
        --disabled-password \
        # will not create a home directory for the user
        --no-create-home \
        # provide the user name
        django-user

# make the python commands execute using the vitural environment
ENV PATH="/py/bin:$PATH"

# switch to this user from root
USER django-user