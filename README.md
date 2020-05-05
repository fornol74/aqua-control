# aqua-control
Installation

Clone repository.

Install python dependicies:

'''
pip3 install PCA9685-driver
pip3 install w1thermsensor
pip3 install gpiozero
'''

Copy service file to systemd folder.

'''
cp aqua-control.service /etc/systemd/system
'''

Edit config.ini file so it works with your system.

Enable and start service.

'''
systemctl enable aqua-control
systemctl start aqua-control
'''

Your aquarium is now under control.
