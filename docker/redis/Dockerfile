FROM redis:5.0.8

RUN apt-get update ;\
    apt-get install -y gettext-base=0.19.8.1-9 dos2unix=7.4.0-1

COPY redis.conf /usr/local/etc/redis/redis.conf.tmp

COPY docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh
RUN dos2unix /usr/local/bin/docker-entrypoint.sh
RUN chmod +x /usr/local/bin/docker-entrypoint.sh
RUN ln -sf /usr/local/bin/docker-entrypoint.sh /