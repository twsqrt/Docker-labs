#!/bin/bash

# Запускаем svale-ов.
# В качестве параметра передаём номер порта, через который будет происходить взаимодействие.
docker run -d --net=map-reduse-net --net-alias=slave_1 slave 8080
docker run -d --net=map-reduse-net --net-alias=slave_2 slave 8080

# Запускаем master-а.
# Передаём в качестве параметров адреса slave-ов в докер сети.
# Также перенаправляем stdin в файл links.txt, в котором находятся ссылки.
docker run --net=map-reduse-net master slave_1:8080 slave_2:8080 < links.txt