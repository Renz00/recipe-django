# We use unprivileged to limit access for security reasons.
FROM nginxinc/nginx-unprivileged:1-alpine
LABEL maintainer="renz00"

# copy the nginx configuration file to the nginx directory
COPY ./default.conf.tpl /etc/nginx/default.conf.tpl
COPY ./uwsgi_params /etc/nginx/uwsgi_params
COPY ./run.sh /run.sh

# Setting the environment variables for the nginx config
ENV LISTEN_PORT=8000
ENV APP_HOST=app
ENV APP_PORT=9000

# switch to root user to create the directories
USER root

RUN mkdir -p /vol/static && \
    chmod 755 /vol/static && \
    # Create the conf file and set the user (ngnix) as owner
    # for running the run.sh script later
    touch /etc/nginx/conf.d/default.conf && \
    chown nginx:nginx /etc/nginx/conf.d/default.conf && \
    # Make the script executable for the user
    chmod +x /run.sh

# Create a volume for the static files
VOLUME /vol/static

# Switch to the nginx user
USER nginx

CMD ["/run.sh"]