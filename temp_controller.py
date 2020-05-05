# temperature read on 1-Wire
from w1thermsensor import W1ThermSensor


class Temp(object):
    def __init__(self, name, data):
        # super().__init__()
        self.name = name
        self.data = []
        self.control = "None"
        self.sensor = W1ThermSensor()
        for details in data:
            if details[0] == "type":
                self.type = details[1]
            if details[0] == "domoticz_id":
                self.domoticz_id = details[1]
            if details[0] == "max":
                self.max = float(details[1])
            if details[0] == "min":
                self.min = float(details[1])
            if details[0] == "hysteresis":
                self.hysteresis = float(details[1])
            if details[0] == "control":
                self.control = details[1]
            if details[0] == "update_count":
                self.update_count = int(details[1])
                self.update_counter = int(details[1])
