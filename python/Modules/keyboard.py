# Modules/keyboard.py
"""
Keyboard handling module using PsychoPy IOHub for precise key timing.
This module is responsible solely for keyboard initialization and event retrieval.
PsychoPy window creation and display management should be handled elsewhere (e.g., display.py).
"""
import logging
from typing import Optional, Tuple, List
from psychopy import visual, core, event

try:
    from psychopy.iohub import launchHubServer
    IOHUB_AVAILABLE = True
except ImportError:
    IOHUB_AVAILABLE = False

#=======CONSTANTS========
KEY_PRESS = 22
KEY_RELEASE = 23
#========================

class QuitSignal(Exception):
    """Raised when the user requests to quit (e.g., ESC or 'q')."""
    pass

def init_keyboard() -> Tuple[Optional[object], Optional[object]]:
    """
    Initialize IOHub server keyboard interface.
    Always tries IOHub; warns if not available (falls back to event).
    """
    if IOHUB_AVAILABLE:
        try:
            io = launchHubServer()
            kb = io.devices.keyboard
            kb.clearEvents()
            logging.info("IOHub keyboard initialized.")
            return kb, io
        except Exception as e:
            logging.error(f"IOHub failed to launch: {e}. Falling back to PsychoPy event (NOT recommended).")
            return None, None
    else:
        logging.warning("IOHub not available: falling back to PsychoPy event module (timings may be inaccurate).")
        return None, None


def clear_events(kb: Optional[object], io: Optional[object]) -> None:
    """
    Clear previous keyboard events.
    """
    if io:
        io.clearEvents()
    elif kb:
        try:
            kb.clearEvents()
        except Exception:
            pass
    else:
        event.clearEvents(eventType='keyboard')


def poll_keys(kb: Optional[object], io: Optional[object]) -> List[object]:
    """
    Poll keyboard events without blocking.

    Returns:
        List of event objects.
    """

    if io and kb:
        events = kb.getEvents()
        for ev in events:
            key = ev.key if hasattr(ev, 'key') else ev
            if key == 'escape':
                raise QuitSignal()
                return 0
        return events
    return event.getKeys()

