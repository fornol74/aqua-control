#!/bin/bash

apt install memcached
apt install python3-pip
apt install build-essential libi2c-dev i2c-tools python-dev libffi-dev

pip3 install PCA9685-driver
pip3 install w1thermsensor
pip3 install gpiozero
pip3 install pymemcache


rm -rf /usr/local/bin/aqua-control
cp -r ./aqua-control /usr/local/bin

cp ./system/aqua_control.service /etc/systemd/system

systemctl enable aqua_control.service
