server {
    listen ${LISTEN_PORT};

    # location is used for mapping urls to different paths
    # the location is checked from top to bottom
    location /static {
        # any url with /static will be mapped to /vol/static
        # This is the volume that contains all static files for the app
        alias /vol/static;
    }

    # This will handle all request not handled by the above
    location / {
        # this is the config for the uWSGI server
        uwsgi_pass  ${APP_HOST}:${APP_PORT}
        # this is needed to include the uwsgi params
        include     /etc/nginx/uwsgi_params;
        # the maximum body size of requests (files should be 10MB or less)
        client_max_body_size 10M;
    }
}