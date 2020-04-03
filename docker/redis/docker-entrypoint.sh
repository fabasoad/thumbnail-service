#!/bin/bash
envsubst < /usr/local/etc/redis/redis.conf.tmp > /usr/local/etc/redis/redis.conf
rm /usr/local/etc/redis/redis.conf.tmp
redis-server /usr/local/etc/redis/redis.conf