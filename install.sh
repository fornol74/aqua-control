#!/bin/bash

apt install memcached
apt install python3-pip

pip3 install PCA9685-driver
pip3 install w1thermsensor
pip3 install gpiozero
pip3 install pymemcache


rm -rf /usr/local/bin/aqua-control
cp -r ./aqua-control /usr/local/bin

cp ./system/aqua_control.service /etc/systemd/system

systemctl enable aqua_control.service
