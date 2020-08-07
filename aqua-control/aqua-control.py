import configparser
from datetime import datetime
from os import system, name
import sys
import time
import threading
import requests

# import memcache
from pymemcache.client import base

# PCA9685 PWM controller
from pca9685_controller import PCA9685

from temp_controller import Temp

from server_controller import cherrypy, HelloWorld, AquaControlServer


# Controll for GPIO on RPi
from gpiozero import DigitalOutputDevice as Output

from pwm_controller import PWM


class Light(object):
    def __init__(self, name, data):
        self.name = name
        self.data = []
        self.max = "100%"
        self.levels = 0
        self.domoticz_id = 0
        for details in data:
            if details[0] == 'type':
                self.type = details[1]
            if details[0] == 'channel':
                self.channel = details[1]
            if details[0] == "domoticz_id":
                self.domoticz_id = details[1]
            if details[0] == 'levels':
                self.levels = int(details[1]) - 1
            if details[0] == 'max':
                if details[1][-1:] == '%':
                    self.max = (int(details[1][:-1])/100)*self.levels
                    print(self.max)
                else:
                    self.max = int(details[1])
                    print(self.max)
            if ':' in details[0]:
                self.data.append(
                    [(sum(int(x) * 60 ** i for i, x in enumerate(reversed(details[0].split(":"))))), (int(details[1])/100)*self.levels])

    def set(self, now):
        """
        Returns status of light object at specified time.
        """

        if now <= min([time for time, value in self.data]):
            value = [value for time, value in self.data if time ==
                     min([time for time, value in self.data])][0]
        # else:
        elif now >= max([time for time, value in self.data]):
            value = [value for time, value in self.data if time ==
                     max([time for time, value in self.data])][0]
        else:
            value1 = [value for time, value in self.data if time > now][0]
            value2 = [value for time, value in self.data if time <= now][len(
                [value for time, value in self.data if time <= now])-1]
            time1 = [time for time, value in self.data if time > now][0]
            time2 = [time for time, value in self.data if time <= now][len(
                [value for time, value in self.data if time <= now])-1]

            value = (((value1-value2)/(time1-time2))*now) + \
                (value1-(((value1-value2)/(time1-time2))*time1))

        if value > self.max:
            value = self.max

        return int(value)


class Switch(object):
    def __init__(self, name, data):
        self.name = name
        self.temp_controlled = False
        self.data = []
        for details in data:
            if details[0] == 'type':
                self.type = details[1]
            if ':' in details[0]:
                self.data.append(
                    [(sum(int(x) * 60 ** i for i, x in enumerate(reversed(details[0].split(":"))))), (details[1])])

    def status(self, now):
        """
        Returns status of switch object at specified time.
        """

        # Assumes that initial state is "off"
        if now < min([time for time, value in self.data]):
            value = "off"
        # Assumes that final state is "off"
        elif now > max([time for time, value in self.data]):
            value = "off"
        else:
            value = [value for time, value in self.data if time <= now][len(
                [value for time, value in self.data if time <= now])-1]
        if self.temp_controlled == True:
            value = "on"
        return value

    def set_temp_control(self, control):
        self.temp_controlled = control


class Pwm(object):
    def __init__(self, name, data):
        self.name = name
        self.data = []
        self.channel = PWM(0)
        for details in data:
            if details[0] == 'output':
                self.output = details[1]
            if details[0] == 'type':
                self.type = details[1]
            if details[0] == 'period':
                self.period = details[1]
            if details[0] == 'duty_cycle':
                self.duty_cycle = details[1]


# Global settings
lights = []
outputs = []
switches = []
temps = []
pwms = []
# domoticz_temp_ready = False
# domoticz_temp = 0.0
domoticz_data = []
domoticz_sever = ""
domoticz_port = ""
pwm_pca_freq = 60
pwm_pca = PCA9685(0x40, pwm_pca_freq)
server_host = ""
server_port = ""


def ini_load():
    """
    Loads parameters from config file.
    """

    global domoticz_sever
    global domoticz_port
    global server_host
    global server_port
    global lights, outputs, switches, temps, domoticz_data, pwms

    result = str(client.get('ini_reload'))

    if result == "b'true'":
        client.set('ini_reload', 'false')
        lights = []
        outputs = []
        switches = []
        temps = []
        pwms = []
        domoticz_data = []
        print("Settings reinitialized")

    config = configparser.ConfigParser(delimiters=('='), interpolation=None)

    config.read('config.ini')

    for sections in config.sections():

        ini_data = [details for details in config.items(sections)]

        if ('type', 'light') in ini_data:
            lights.append(Light(sections, ini_data))
            for data in ini_data:
                if data[0].upper() == "DOMOTICZ_ID":
                    domoticz_id = data[1]
                    """
                    Inicjuje listę domoticz_data wartościami:
                    domoticz_id = numer sensora domoticza na podstawie pliku .ini
                    druga wartość domoticz type na podstawie grupy .ini
                    trzecie wartość początkowa wartość temperatury
                    czwarta wartość czy temperatura została zaktualizowana i można wysłać do domoticza
                    """
                    domoticz_data.append(
                        [domoticz_id, "LIGHT", 0.0, False])

        if ('type', 'switch') in ini_data:
            switches.append(Switch(sections, ini_data))

        if ('type', 'pwm') in ini_data:
            pwms.append(Pwm(sections, ini_data))

            for pwm in pwms:
                pwm.channel.export()
                pwm.channel.period = int(pwm.period)
                pwm.channel.duty_cycle = int(pwm.duty_cycle)

        if ('type', 'temp') in ini_data:
            temps.append(Temp(sections, ini_data))
            for data in ini_data:
                if data[0].upper() == "DOMOTICZ_ID":
                    domoticz_id = data[1]
                    """
                    Inicjuje listę domoticz_data wartościami:
                    domoticz_id = numer sensora domoticza na podstawie pliku .ini
                    druga wartość domoticz type na podstawie grupy .ini
                    trzecie wartość początkowa wartość temperatury
                    czwarta wartość czy temperatura została zaktualizowana i można wysłać do domoticza
                    """
                    domoticz_data.append(
                        [domoticz_id, "TEMP", 0.0, False])

        if ('GPIO_OUTPUT') in sections:
            for data in ini_data:
                if data[1] != "18":
                    outputs.append(
                        [data[0].upper(), Output(int(data[1]))])

        if ('DOMOTICZ') in sections:
            for data in ini_data:
                if data[0].upper() == "SERVER":
                    domoticz_sever = data[1]
                if data[0].upper() == "PORT":
                    domoticz_port = data[1]

        if ('GENERAL') in sections:
            for data in ini_data:
                if data[0].upper() == "SERVER_HOST":
                    server_host = str(data[1])
                if data[0].upper() == "SERVER_PORT":
                    server_port = int(data[1])


def domoticz_loop():
    """
    Procedure updates domoticz sensor.
    General update code is as follows:
    /json.htm?type=command&param=udevice&idx=IDX&nvalue=0&svalue=TEMP
    """

    global domoticz_sever
    global domoticz_port
    # global domoticz_temp_ready
    # global domoticz_temp

    while True:
        print("domoticz loop")
        for data in domoticz_data:
            print(data[1])
            print(data[3])
            try:
                if data[1] == "TEMP" and data[3] == True:
                    domoticz_resp = requests.get("http://"+domoticz_sever+":"+domoticz_port +
                                                 "/json.htm?type=command&param=udevice&idx=" +
                                                 str(data[0])+"&nvalue=0&svalue=" +
                                                 str(data[2]))
                    data[3] = False
                    print("Domoticz light update")
                    print(domoticz_resp.status_code)

                # custom sensor udpate
                # /json.htm?type=command&param=udevice&idx=IDX&nvalue=0&svalue=VALUE
                if data[1] == "LIGHT" and data[3] == True:
                    domoticz_resp = requests.get("http://"+domoticz_sever+":"+domoticz_port +
                                                 "/json.htm?type=command&param=udevice&idx=" +
                                                 str(data[0])+"&nvalue=0&svalue=" +
                                                 str(data[2]))
                    data[3] = False
                    print("Domoticz temp update")
                    print(domoticz_resp.status_code)
            except:
                pass
        time.sleep(10)


def temp_loop():
    """
    Reads temperature sensor
    """
    while True:
        # temp controll
        # global domoticz_temp_ready
        # global domoticz_temp

        for temp in temps:
            # print(temp.name)
            temp.update_counter -= 1
            if temp.update_counter <= 0:
                temp.update_counter = temp.update_count
                temperature = temp.sensor.get_temperature()
                # domoticz_temp = temperature
                # domoticz_temp_ready = True
                for data in domoticz_data:
                    if data[0] == temp.domoticz_id:
                        data[2] = temperature
                        data[3] = True
                print(temperature)
                if temperature > temp.max + temp.hysteresis:
                    if temp.control != "None":
                        # [pin.on()
                        #  for name, pin in outputs if name == temp.control]
                        [switch.set_temp_control(
                            True) for switch in switches if switch.name == temp.control]
                        # print("temp loop")
                        # [print(switch.temp_controlled)
                        #  for switch in switches if switch.name == temp.control]
                if temperature < temp.max:
                    if temp.control != "None":
                        # [pin.off()
                        #  for name, pin in outputs if name == temp.control]
                        [switch.set_temp_control(
                            False) for switch in switches if switch.name == temp.control]
                        # print("temp loop")
                        # [print(switch.temp_controlled)
                        #  for switch in switches if switch.name == temp.control]


# def main_loop():
#     """
#     This procedures just triggers main procedure
#     """

#     # global ini_reload
#     while True:
#         time.sleep(0.5)
#         main()

#         result = str(client.get('ini_reload'))

#         if result == "b'true'":
#             ini_load()


def main():
    """
    Main loop
    Controls lighs and switches
    """

    print("Main loop start")

    try:
        print("now - main")
        now = (sum(int(x) * 60 ** i for i,
                   x in enumerate(reversed(datetime.now().strftime("%H:%M:%S").split(":")))))
        print(now)
    except:
        print("now - exception")

    # control of lights
    try:
        print("lights - main")
        for light in lights:
            light_value = light.set(now)
            pwm_pca.set_pwm(int(light.channel), light_value)

            for data in domoticz_data:
                if data[0] == light.domoticz_id:
                    data[2] = light_value
                    data[3] = True

            print(light.set(now))
    except:
        print("lights - exception")

    # Control of switches - devices connected to GPIO pins
    try:
        print("switches - main")
        for switch in switches:
            switch_name = switch.name
            status = switch.status(now)
            # print("switch loop")
            # print(switch.temp_controlled)
            # if switch.temp_controlled != True:
            if status == "on":
                print("Status on")
                if not pwms:
                    [pin.on() for name, pin in outputs if name == switch_name]
                else:
                    for pwm in pwms:
                        if pwm.output == switch_name:
                            print("test pwm on")
                            pwm.channel.enable = True
                        else:
                            print("test gpio on")
                            [pin.on() for name, pin in outputs if name == switch_name]
            if status == "off":
                print("Status off")
                if not pwms:
                    [pin.off() for name, pin in outputs if name == switch_name]
                else: 
                    for pwm in pwms:
                        if pwm.output == switch_name:
                            print("test off")
                            pwm.channel.enable = False
                        else:
                            print("test gpio off")
                            [pin.off() for name, pin in outputs if name == switch_name]
    except:
        print("switches - exception")


def cherrypy_run(sever_host, server_port):
    cherrypy.quickstart(AquaControlServer(
    ), '/', {'global': {'server.socket_host': server_host, 'server.socket_port': server_port}})


if __name__ == '__main__':
    client = base.Client(('127.0.0.1', 11211))

    ini_load()

    cherrypy_app_start = threading.Thread(
        target=cherrypy_run, args=(server_host, server_port, ))
    cherrypy_app_start.start()

    temp_loop = threading.Thread(target=temp_loop)
    temp_loop.start()

    # main_loop_thread = threading.Thread(target=main_loop)
    # main_loop_thread.start()

    domoticz_loop_thread = threading.Thread(target=domoticz_loop)
    domoticz_loop_thread.start()

    while True:
        result = str(client.get('ini_reload'))

        if result == "b'true'":
            ini_load()

        main()

        time.sleep(0.5)

    # while True:
    #     # # for windows
    #     # if name == 'nt':
    #     #     _ = system('cls')

    #     # # for mac and linux(here, os.name is 'posix')
    #     # else:
    #     #     _ = system('clear')

    #     time1 = datetime.now()
    #     main()
    #     time.sleep(0.5)
    #     print(datetime.now()-time1)
