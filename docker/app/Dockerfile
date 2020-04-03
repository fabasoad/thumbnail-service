FROM python:3.9.0a5-buster

RUN apt-get update ;\
    apt-get install -y dos2unix=7.4.0-1

COPY docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh
RUN dos2unix /usr/local/bin/docker-entrypoint.sh
RUN chmod +x /usr/local/bin/docker-entrypoint.sh
RUN ln -sf /usr/local/bin/docker-entrypoint.sh /