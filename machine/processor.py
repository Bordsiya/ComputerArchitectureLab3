from machine.control_unit import ControlUnit
from machine.memory import Memory
from machine.tact_generator import TactGenerator


class Processor:

    def __init__(self, device):
        self.tact_generator = TactGenerator()
        self.memory = Memory()
        self.device = device
        self.control_unit = ControlUnit(self.tact_generator, self.memory, self.device)

    def start(self, ip):
        self.control_unit.clean_logs()
        self.device.io = ip
        self.tact_generator.clean_tact()
        self.control_unit.set_start_ip()
        self.control_unit.command_fetch()
