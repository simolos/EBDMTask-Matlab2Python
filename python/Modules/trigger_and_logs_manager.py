# trigger_and_logs_manager.py
from psychopy import parallel, core
import threading
import queue
import time
import sys
from enum import IntEnum
import pandas as pd

try:
    import serial
except ImportError as e:
    raise ImportError(
        "Need to install pyserial with `pip install pyserial`"
    )

# --- Trigger codes ---
class TriggerCodes(IntEnum):
    TI = 1                   # MRI trigger / scanner sync
    PREP_DM = 2
    DM = 3   # Offer appears on screen
    DECISION_MADE = 4       # Decision onset
  

# --- TriggerManager class ---
class TriggerManager:
    """
    Asynchronous trigger manager for parallel (MRI, TMSroom) or serial (Arduino) port.
    Supports full time logging:
     - requested_time = when the main behavioral task requested the trigger
     - start_time = when the worker thread started handling the trigger 
     - end_time = when the trigger command finished (sending to the hardware, not executing by the hardware!!!)
    All Timestamps are relative to the first trigger (time zero).
    """
    def __init__(self, mode="log_only", port=None, serial_port=None, pulse_width=0.005, enabled=True):

        self.mode = mode
        self.port = port
        self.serial = serial_port
        self.pulse_width = pulse_width
        self.enabled = enabled

        self.queue = queue.Queue()
        self.running = True
        self._start_time = None  # time of first trigger

        self.trigger_log = []  # log of all triggers

        self.thread = threading.Thread(target=self._worker, daemon=True)
        self.thread.start()

    def send(self, code, width=None):
        """Queue a trigger event without blocking."""
        if width is None:
            width = self.pulse_width
        requested_time = time.perf_counter()
        self.queue.put((code, width, requested_time))

    def _worker(self):
        while self.running:
            code, width, requested_time = self.queue.get()
            if code is None:
                break

            start_time = time.perf_counter()

            # Set first trigger as time zero
            if self._start_time is None:
                self._start_time = start_time
            relative_requested = requested_time - self._start_time
            relative_start = start_time - self._start_time

            # Hardware write
            if self.enabled:
                try:
                    if self.mode == "parallel" and self.port is not None:
                        self.port.setData(code)
                        core.wait(width)
                        self.port.setData(0)
                    elif self.mode == "arduino" and self.serial is not None:
                        self.serial.write(bytes([code]))
                        # Optionally: could wait for ACK here for exact end_time
                except Exception as e:
                    print(f"TriggerManager error sending code {code}: {e}")

            end_time = time.perf_counter() - self._start_time

            # Log times relative to first trigger
            self.trigger_log.append({
                "code": code,
                "requested_time": relative_requested,
                "start_time": relative_start,
                "end_time": end_time
            })

            self.queue.task_done()

    def close(self):
        """Stop worker thread and close serial if needed."""
        self.running = False
        self.queue.put((None, None, None))
        self.thread.join()
        if self.mode == "arduino" and self.serial is not None and self.enabled:
            try:
                self.serial.close()
            except Exception as e:
                print(f"Error closing serial port: {e}")

    def get_log_dataframe(self):
        """Return the trigger log as a pandas DataFrame."""
        if not self.trigger_log:
            return pd.DataFrame(columns=["code", "requested_time", "start_time", "end_time"])
        return pd.DataFrame(self.trigger_log)

    @property
    def start_time(self):
        """Return the absolute perf_counter of the first trigger (None if none sent yet)."""
        return self._start_time


# --- Factory function ---
def init_triggers(cfg):
    """
    Initialize TriggerManager based on experiment config.
    Returns a TriggerManager instance:
      - with hardware if available,
      - or log-only if hardware unavailable.

    """
    # MRI: parallel port triggers
    if cfg.experiment == "MRI":
        if sys.platform == 'darwin':
            print("macOS: parallel port unavailable --> log-only)")
            return TriggerManager(mode="log_only", simulate_hadware=False)
        port = parallel.ParallelPort(address=0x7FF0)
        return TriggerManager(mode="parallel", port=port, pulse_width=0.005)

    # Arduino setup
    elif cfg.experiment == "DBS":
        try:
            # Attempt to open the Arduino port
            ser = serial.Serial('/dev/ttyACM0', 115200)
        except serial.SerialException as e:
            # Fail if Arduino is not connected/detected
            raise RuntimeError(
                "Arduino not detected on /dev/ttyACM0. "
                "Connect the device or change the port. "
                "If you are running in test mode, use log_only mode."
            ) from e

        return TriggerManager(mode="DBS", serial_port=ser)

    else:
        print("No trigger hardware configured (log-only)")
        return TriggerManager(mode="log_only", enabled=False)