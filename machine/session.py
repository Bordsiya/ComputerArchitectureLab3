from machine.device import Device
from machine.processor import Processor


class Session:

    def __init__(self):
        self.device = Device()
        self.processor = Processor(self.device)

    def load(self, instructions):
        self.device.io = 0
        self.processor.control_unit.set_start_ip()
        for instruction in instructions:
            self.device.io = instruction
            self.processor.control_unit.input()

    def run(self, ip):
        self.processor.start(ip)
