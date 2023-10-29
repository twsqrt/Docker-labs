#!/bin/bash

# Запускаем svale-ов.
# В качестве параметра передаём номер порта, через который будет происходить взаимодействие.
docker run -d --net=map-reduse-net --net-alias=first map-reduse:slave 8080
docker run -d --net=map-reduse-net --net-alias=second map-reduse:slave 8080

# Запускаем master-а.
# Передаём в качестве параметров адреса slave-ов в докер сети.
docker run --net=map-reduse-net map-reduse:master first:8080 second:8080

# Результат работы master-а:

# send page: https://en.wikipedia.org/wiki/KEK
# send page: https://en.wikipedia.org/wiki/Ramanujan_theta_function
# send page: https://en.wikipedia.org/wiki/Srinivasa_Ramanujan
# result:
# the	 matches:576
# of	 matches:369
# ramanujan	 matches:357
# a	 matches:343
# and	 matches:288
# in	 matches:267
# to	 matches:248
# 2	 matches:229
# 1	 matches:152
# his	 matches:146
# 's	 matches:142
# on	 matches:138
# was	 matches:114
# frac	 matches:112
# for	 matches:102
# he	 matches:97
# 4	 matches:94
# that	 matches:89
# e	 matches:88
# from	 matches:86
# π	 matches:86
# q	 matches:79
# p	 matches:76
# hardy	 matches:75
# t	 matches:74
# by	 matches:72
# b	 matches:70
# at	 matches:67
# left	 matches:67
# is	 matches:66