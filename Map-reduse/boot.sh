#!/bin/bash

# Создаём сеть, через которую будут общаться контейтеры.
docker network create -d bridge map-reduse-net

# Создаём контейнеры master и slave.
docker build --no-cache=true -t map-reduse:slave ./slave
docker build --no-cache=true -t map-reduse:master ./master