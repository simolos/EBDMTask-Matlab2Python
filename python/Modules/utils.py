# utils.py
from psychopy import parallel, core
import sys


class ParallelTrigger:
    def __init__(self, address=0x7FF0):
        # address being the parallel port base address

        self.port = parallel.ParallelPort(address=address)
        
        # macOS: parallel port not available
        if sys.platform == 'darwin':
            print('macOS, cannot send TI trigger through parallel port!')
            self.enabled = False
            return

    def send(self, code=1, width=0.05):

        if not self.enabled or self.port is None:
            return

        # rising edge
        self.port.setData(code)
        core.wait(width)
        # falling edge
        self.port.setData(0)

