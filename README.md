## Equipment list:

1. Raspberry itself - should work really with any.
2. To work with lights you will need PCA9685 PWM controller connected to your RPi and lights connected to it (through some transistors).
3. Dallas DS18B20 (in water proof configuration) is used as temperature sensor.
4. Devices like fans are controlled directly through GPIO pins but with use of some relay shield.

Some new features and improvements

5. I use Raspberry's PWM hardware controller for some devices. It supports very high frequencies (tested up to 30 kHz) what results in very smooth operation of controlled fans. All credits go to:
   https://jumpnowtek.com/rpi/Using-the-Raspberry-Pi-Hardware-PWM-timers.html.
   I use Python class from the link above with just change file name.
   Note: only some pins of RPi can be controlled this way.
6. For lights you can specify number of available control steps (4095 in case of PCA9685). When specifing maximum control limit you can use percentage or absolute values.
7. Thanks to CherryPy library program creates small web server. At the moment its functionality is limited to .ini file editing.
8. Some directory structure was created.
   `aqua-control`folder consist program itself. `system` folder consist service that shall be copied to /etc/systemd/system/ folder of OS.
9. Some small installation script (`install.sh`) was created.

## Installation

Clone repository.

Run:

```
./install.sh
```

It will try to install required software and Python libraries. At the end it will enable daemon to run program in the background.

Remember to start it with:

```
systemctl start aqua_control
```

Your aquarium is now under control.

This is considered under construction. Code is not polished, still many comments in it and test print outs. But it works. Code is greatly inspired by reef-pi project: https://reef-pi.github.io/. If you do not know how to use above maybe you should consider reef-pi instead.
