from pca9685_driver import Device


class PCA9685(Device):
    def __init__(self, address, frequency):
        super().__init__(address)
        # Device.__init__(self, address)
        self.set_pwm_frequency(frequency)

    def pca9685_set(self, channel, value):
        self.set_pwm(channel, value)
