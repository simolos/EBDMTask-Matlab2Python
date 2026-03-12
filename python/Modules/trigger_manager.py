import threading
import queue
import time


class TriggerManager:

    def __init__(self, mode="parallel", port=None, serial=None, pulse_width=0.005):
        """
        mode: 'parallel' or 'arduino'
        port: parallel port object (e.g. psychopy.parallel.ParallelPort)
        serial: serial object (pyserial)
        pulse_width: pulse duration for parallel triggers
        """

        self.mode = mode
        self.port = port
        self.serial = serial
        self.pulse_width = pulse_width

        self.queue = queue.Queue()
        self.running = True

        self.thread = threading.Thread(target=self._worker, daemon=True)
        self.thread.start()

    def send(self, code):
        """Queue trigger without blocking the experiment."""
        timestamp = time.perf_counter()
        self.queue.put((code, timestamp))

    def _worker(self):

        while self.running:

            code, timestamp = self.queue.get()

            if code is None:
                break

            if self.mode == "parallel":

                self.port.setData(code)
                time.sleep(self.pulse_width)
                self.port.setData(0)

            elif self.mode == "arduino":

                self.serial.write(bytes([code]))

            self.queue.task_done()

    def close(self):

        self.running = False
        self.queue.put((None, None))
        self.thread.join()