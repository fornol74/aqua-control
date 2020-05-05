## Equipment list:

1. Raspberry itself - should work really with any.
2. To work with lights you will need PCA9685 PWM controller connected to your RPi and lights connected to it (through some transistors).
3. Dallas DS18B20 (in water proof configuration) is used as temperature sensor.
4. Devices like fans are controlled directly through GPIO pins but with use of some relay shield.

## Installation

Clone repository.

Install python dependicies:

```
pip3 install PCA9685-driver
pip3 install w1thermsensor
pip3 install gpiozero
```

Copy service file to systemd folder.

```
cp aqua-control.service /etc/systemd/system
```

Edit config.ini file so it works with your system.

Enable and start service.

```
systemctl enable aqua-control
systemctl start aqua-control
```

Your aquarium is now under control.
