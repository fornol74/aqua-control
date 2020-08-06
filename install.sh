#!/bin/bash

apt install memcached
apt install python3-pip

#Below is required by PCA9685-driver
apt install build-essential libi2c-dev i2c-tools python-dev libffi-dev

#enable i2c
sed -i 's/#dtparam=i2c_arm=on/dtparam=i2c_arm=on/' /boot/config.txt

#enable 1-wire
grep -q '^dtoverlay=w1-gpio' /boot/config.txt || echo 'dtoverlay=w1-gpio' >> /boot/config.txt

#enable hardware pwm
grep -q '^dtoverlay=pwm' /boot/config.txt || echo 'dtoverlay=pwm' >> /boot/config.txt

pip3 install PCA9685-driver
pip3 install w1thermsensor
pip3 install gpiozero
pip3 install pymemcache


rm -rf /usr/local/bin/aqua-control
cp -r ./aqua-control /usr/local/bin

cp ./system/aqua_control.service /etc/systemd/system

systemctl enable aqua_control.service

echo "Please reboot your system"
