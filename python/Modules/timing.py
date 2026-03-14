## timing.py

from psychopy import core
from keyboard import poll_keys

def wait_with_escape(seconds, kb, io):
    """Busy-wait while polling keys so ESC/QuitSignal is honored."""
    end_t = core.getTime() + float(seconds)

    while core.getTime() < end_t:
        _ = poll_keys(kb, io)
        core.wait(0.001)